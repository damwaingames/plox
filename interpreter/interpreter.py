from math import isnan
from typing import Any

from abstract_syntax_tree import (
    Expr,
    Binary,
    Grouping,
    Literal,
    Unary,
    Stmt,
    Expression,
    Print,
)
from errors import ErrorHandler, LoxRuntimeError
from scanner.token import Token, TokenType


class Interpreter:
    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeError as e:
            ErrorHandler.runtime_error(e)

    def _execute(self, statement: Stmt) -> Any:
        match statement:
            case Expression():
                self._evaluate(statement._expression)
                return None
            case Print():
                value = self._evaluate(statement._expression)
                print(self._stringify(value))
                return None

    def _evaluate(self, expression: Expr) -> Any:
        match expression:
            case Binary():
                left = self._evaluate(expression._left)
                right = self._evaluate(expression._right)
                match expression._operator.type:
                    case TokenType.BANG_EQUAL:
                        return not self._is_equal(left, right)
                    case TokenType.EQUAL_EQUAL:
                        return self._is_equal(left, right)
                    case TokenType.GREATER:
                        self._check_number_operands(expression._operator, left, right)
                        return float(left) > float(right)
                    case TokenType.GREATER_EQUAL:
                        self._check_number_operands(expression._operator, left, right)
                        return float(left) >= float(right)
                    case TokenType.LESS:
                        self._check_number_operands(expression._operator, left, right)
                        return float(left) < float(right)
                    case TokenType.LESS_EQUAL:
                        self._check_number_operands(expression._operator, left, right)
                        return float(left) <= float(right)
                    case TokenType.MINUS:
                        self._check_number_operands(expression._operator, left, right)
                        return float(left) - float(right)
                    case TokenType.PLUS:
                        if isinstance(left, float) and isinstance(right, float):
                            return float(left) + float(right)
                        if isinstance(left, str) and isinstance(right, str):
                            return str(left) + str(right)
                        raise LoxRuntimeError(
                            expression._operator,
                            "Operands must be two numbers or two strings.",
                        )
                    case TokenType.SLASH:
                        self._check_number_operands(expression._operator, left, right)
                        try:
                            return float(left) / float(right)
                        except ZeroDivisionError:
                            return float("nan")
                    case TokenType.STAR:
                        self._check_number_operands(expression._operator, left, right)
                        return float(left) * float(right)
            case Grouping():
                return self._evaluate(expression._expression)
            case Literal():
                return expression._value
            case Unary():
                right = self._evaluate(expression._right)
                match expression._operator.type:
                    case TokenType.BANG:
                        return not self._is_truthy(right)
                    case TokenType.MINUS:
                        self._check_number_operand(expression._operator, right)
                        return -int(right)
            case _:
                raise NotImplementedError(
                    f"Not added a case for a certain expression : {expression}"
                )

    def _is_truthy(self, object: Any) -> bool:
        if object is None:
            return False
        if isinstance(object, bool):
            return object
        return True

    def _is_equal(self, a: Any, b: Any):
        if isinstance(a, float) and isinstance(b, float):
            # This is needed for the IEEE 754 non compliance of Lox
            if isnan(a) and isnan(b):
                return True
        return a == b if type(a) == type(b) else False

    def _check_number_operand(self, operator: Token, operand: Any) -> None:
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(operand, "Operand must be a number.")

    def _check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operands must be numbers.")

    def _stringify(self, object: Any) -> str:
        if object is None:
            return "nil"
        if isinstance(object, float):
            text = str(object)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        if isinstance(object, bool):
            return str(object).lower()
        return str(object)
