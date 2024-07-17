from collections import deque
from enum import auto, Enum

from abstract_syntax_tree.expressions import (
    Assign,
    Binary,
    Call,
    Expr,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Unary,
    Variable,
)
from abstract_syntax_tree.statements import (
    Block,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Stmt,
    Var,
    While,
)
from errors import ErrorHandler
from interpreter import Interpreter
from scanner.token import Token


class Resolver(Expr.Visitor[None], Stmt.Visitor[None]):
    class FunctionType(Enum):
        NONE = auto()
        FUNCTION = auto()
        METHOD = auto()

    def __init__(self, interpreter: Interpreter) -> None:
        self._interpreter = interpreter
        self._scopes: deque[dict[str, bool]] = deque()
        self._current_function = Resolver.FunctionType.NONE

    def resolve(self, x: Expr | Stmt) -> None:
        x.accept(self)

    def resolve_statements(self, statements: list[Stmt]) -> None:
        for statement in statements:
            self.resolve(statement)

    def _resolve_function(
        self, function: Function, f_type: "Resolver.FunctionType"
    ) -> None:
        enclosing_function = self._current_function
        self._current_function = f_type
        self._begin_scope()
        for param in function._params:
            self._declare(param)
            self._define(param)
        self.resolve_statements(function._body)
        self._end_scope()
        self._current_function = enclosing_function

    def _begin_scope(self) -> None:
        self._scopes.append({})

    def _end_scope(self) -> None:
        self._scopes.pop()

    def _declare(self, name: Token) -> None:
        if not self._scopes:
            return None
        scope = self._scopes[-1]
        if name.lexeme in scope.keys():
            ErrorHandler.error(name, "Already a variable with this name in this scope.")
        scope.update({name.lexeme: False})

    def _define(self, name: Token) -> None:
        if not self._scopes:
            return None
        self._scopes[-1].update({name.lexeme: True})

    def _resolve_local(self, expr: Expr, name: Token):
        for i, scope in enumerate(reversed(self._scopes)):
            if name.lexeme in scope.keys():
                self._interpreter.resolve(expr, i)

    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self.resolve_statements(stmt._statements)
        self._end_scope()

    def visit_class_stmt(self, stmt: Class) -> None:
        self._declare(stmt._name)
        self._define(stmt._name)
        for method in stmt._methods:
            declaration = Resolver.FunctionType.METHOD
            self._resolve_function(method, declaration)

    def visit_function_stmt(self, stmt: Function) -> None:
        self._declare(stmt._name)
        self._define(stmt._name)
        self._resolve_function(stmt, Resolver.FunctionType.FUNCTION)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.resolve(stmt._expression)

    def visit_if_stmt(self, stmt: If) -> None:
        self.resolve(stmt._condition)
        self.resolve(stmt._then_branch)
        if stmt._else_branch:
            self.resolve(stmt._else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        self.resolve(stmt._expression)

    def visit_return_stmt(self, stmt: Return) -> None:
        if self._current_function == Resolver.FunctionType.NONE:
            ErrorHandler.error(stmt._keyword, "Can't return from top-level code.")
        if stmt._value is not None:
            self.resolve(stmt._value)

    def visit_var_stmt(self, stmt: Var) -> None:
        self._declare(stmt._name)
        if stmt._initializer is not None:
            self.resolve(stmt._initializer)
        self._define(stmt._name)

    def visit_while_stmt(self, stmt: While) -> None:
        self.resolve(stmt._condition)
        self.resolve(stmt._body)

    def visit_assign_expr(self, expr: Assign) -> None:
        self.resolve(expr._value)
        self._resolve_local(expr, expr._name)

    def visit_binary_expr(self, expr: Binary) -> None:
        self.resolve(expr._left)
        self.resolve(expr._right)

    def visit_call_expr(self, expr: Call) -> None:
        self.resolve(expr._callee)
        for argument in expr._arguments:
            self.resolve(argument)

    def visit_get_expr(self, expr: Get) -> None:
        self.resolve(expr._object)

    def visit_grouping_expr(self, expr: Grouping) -> None:
        self.resolve(expr._expression)

    def visit_literal_expr(self, expr: Literal) -> None:
        pass

    def visit_logical_expr(self, expr: Logical) -> None:
        self.resolve(expr._left)
        self.resolve(expr._right)

    def visit_set_expr(self, expr: Set) -> None:
        self.resolve(expr._value)
        self.resolve(expr._object)

    def visit_unary_expr(self, expr: Unary) -> None:
        self.resolve(expr._right)

    def visit_variable_expr(self, expr: Variable) -> None:
        if self._scopes and self._scopes[-1].get(expr._name.lexeme) is False:
            ErrorHandler.error(
                expr._name, "Can't read local variable in it's own initializer."
            )
        self._resolve_local(expr, expr._name)
