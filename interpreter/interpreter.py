from math import isnan
from typing import Any

from abstract_syntax_tree import (
    Expr,
    Assign,
    Binary,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
    Stmt,
    Block,
    Expression,
    If,
    Print,
    Var,
    While,
)
from environment import Environment
from errors import ErrorHandler, LoxRuntimeError
from scanner.token import Token, TokenType


class Interpreter:
    def __init__(self) -> None:
        self._environment = Environment(None)

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeError as e:
            ErrorHandler.runtime_error(e)

    def _execute(self, statement: Stmt) -> None:
        match statement:
            case Block():
                self._execute_block(
                    statement._statements, Environment(self._environment)
                )
            case Expression():
                self._evaluate(statement._expression)
            case If():
                if self._is_truthy(self._evaluate(statement._condition)):
                    self._execute(statement._then_branch)
                elif statement._else_branch:
                    self._execute(statement._else_branch)
            case Print():
                val = self._evaluate(statement._expression)
                print(self._stringify(val))
            case Var():
                if statement._initializer is not None:
                    value = self._evaluate(statement._initializer)
                else:
                    value = self._evaluate(Literal(None))
                self._environment.define(statement._name.lexeme, value)
            case While():
                while self._is_truthy(self._evaluate(statement._condition)):
                    self._execute(statement._body)

    def _execute_block(self, statements: list[Stmt], environment: Environment) -> None:
        previous = self._environment
        try:
            self._environment = environment
            for statment in statements:
                self._execute(statment)
        finally:
            self._environment = previous

    def _evaluate(self, expression: Expr) -> Any:
        match expression:
            case Assign():
                value = self._evaluate(expression._value)
                self._environment.assign(expression._name, value)
                return value
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
            case Logical():
                left = self._evaluate(expression._left)
                if expression._operator == TokenType.OR:
                    if self._is_truthy(left):
                        return left
                else:
                    if not self._is_truthy(left):
                        return left
                return self._evaluate(expression._right)
            case Unary():
                right = self._evaluate(expression._right)
                match expression._operator.type:
                    case TokenType.BANG:
                        return not self._is_truthy(right)
                    case TokenType.MINUS:
                        self._check_number_operand(expression._operator, right)
                        return -int(right)
            case Variable():
                return self._environment.get(expression._name)
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
        return a == b if type(a) is type(b) else False

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
