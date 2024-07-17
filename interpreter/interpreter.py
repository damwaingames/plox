from math import isnan
from typing import Any

from abstract_syntax_tree.expressions import (
    Expr,
    Assign,
    Binary,
    Call,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from abstract_syntax_tree.statements import (
    Function,
    Return,
    Stmt,
    Block,
    Expression,
    If,
    Print,
    Var,
    While,
)
from environment import Environment
from errors import ErrorHandler, LoxRuntimeError, LoxReturn
from lox_builtins import ClockFunction, LoxCallable, LoxFunction
from scanner.token import Token, TokenType


class Interpreter(Expr.Visitor[Any], Stmt.Visitor[None]):
    def __init__(self) -> None:
        self.globals = Environment(None)
        self._environment = self.globals
        self.globals.define("clock", ClockFunction)

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeError as e:
            ErrorHandler.runtime_error(e)

    def _execute(self, statement: Stmt) -> None:
        statement.accept(self)

    def _evaluate(self, expression: Expr) -> Any:
        return expression.accept(self)

    def _execute_block(self, statements: list[Stmt], environment: Environment) -> None:
        previous = self._environment
        try:
            self._environment = environment
            for statment in statements:
                self._execute(statment)
        finally:
            self._environment = previous

    def visit_block_stmt(self, stmt: Block) -> None:
        self._execute_block(stmt._statements, Environment(self._environment))

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._evaluate(stmt._expression)

    def visit_function_stmt(self, stmt: Function) -> None:
        function = LoxFunction(stmt)
        self._environment.define(stmt._name.lexeme, function)

    def visit_if_stmt(self, stmt: If) -> None:
        if self._is_truthy(self._evaluate(stmt._condition)):
            self._execute(stmt._then_branch)
        elif stmt._else_branch:
            self._execute(stmt._else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        val = self._evaluate(stmt._expression)
        print(self._stringify(val))

    def visit_return_stmt(self, stmt: Return) -> None:
        if stmt._value is not None:
            value = self._evaluate(stmt._value)
        else:
            value = self._evaluate(Literal(None))
        raise LoxReturn(value)

    def visit_var_stmt(self, stmt: Var) -> None:
        if stmt._initializer is not None:
            value = self._evaluate(stmt._initializer)
        else:
            value = self._evaluate(Literal(None))
        self._environment.define(stmt._name.lexeme, value)

    def visit_while_stmt(self, stmt: While) -> None:
        while self._is_truthy(self._evaluate(stmt._condition)):
            self._execute(stmt._body)

    def visit_assign_expr(self, expr: Assign) -> Any:
        value = self._evaluate(expr._value)
        self._environment.assign(expr._name, value)
        return value

    def visit_binary_expr(self, expr: Binary) -> Any:
        left = self._evaluate(expr._left)
        right = self._evaluate(expr._right)
        match expr._operator.type:
            case TokenType.BANG_EQUAL:
                return not self._is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self._is_equal(left, right)
            case TokenType.GREATER:
                self._check_number_operands(expr._operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self._check_number_operands(expr._operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self._check_number_operands(expr._operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self._check_number_operands(expr._operator, left, right)
                return float(left) <= float(right)
            case TokenType.MINUS:
                self._check_number_operands(expr._operator, left, right)
                return float(left) - float(right)
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                raise LoxRuntimeError(
                    expr._operator,
                    "Operands must be two numbers or two strings.",
                )
            case TokenType.SLASH:
                self._check_number_operands(expr._operator, left, right)
                try:
                    return float(left) / float(right)
                except ZeroDivisionError:
                    return float("nan")
            case TokenType.STAR:
                self._check_number_operands(expr._operator, left, right)
                return float(left) * float(right)

    def visit_call_expr(self, expr: Call) -> Any:
        callee = self._evaluate(expr._callee)
        arguments: list[Any] = []
        for argument in expr._arguments:
            arguments.append(self._evaluate(argument))
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr._paren, "Can only call functions and classes.")
        function: LoxCallable = callee
        if len(arguments) != function.arity():
            raise LoxRuntimeError(
                expr._paren,
                f"Expected {function.arity()} arguments but got {len(arguments)}.",
            )
        return function.call(self, arguments)

    def visit_grouping_expr(self, expr: Grouping) -> Any:
        return self._evaluate(expr._expression)

    def visit_literal_expr(self, expr: Literal) -> Any:
        return expr._value

    def visit_logical_expr(self, expr: Logical) -> Any:
        left = self._evaluate(expr._left)
        if expr._operator == TokenType.OR:
            if self._is_truthy(left):
                return left
        else:
            if not self._is_truthy(left):
                return left
        return self._evaluate(expr._right)

    def visit_unary_expr(self, expr: Unary) -> Any:
        right = self._evaluate(expr._right)
        match expr._operator.type:
            case TokenType.BANG:
                return not self._is_truthy(right)
            case TokenType.MINUS:
                self._check_number_operand(expr._operator, right)
                return -int(right)

    def visit_variable_expr(self, expr: Variable) -> Any:
        return self._environment.get(expr._name)

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
