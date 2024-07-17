from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from scanner.token import Token

from .expressions import Expr

R = TypeVar("R")


class Stmt(ABC):
    class Visitor(ABC, Generic[R]):
        @abstractmethod
        def visit_block_stmt(self, stmt: "Block") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_class_stmt(self, stmt: "Class") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_expression_stmt(self, stmt: "Expression") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_function_stmt(self, stmt: "Function") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_if_stmt(self, stmt: "If") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_print_stmt(self, stmt: "Print") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_return_stmt(self, stmt: "Return") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_var_stmt(self, stmt: "Var") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_while_stmt(self, stmt: "While") -> R:
            raise NotImplementedError()

    @abstractmethod
    def accept(self, visitor: Visitor[R]) -> R:
        raise NotImplementedError()


class Block(Stmt):
    def __init__(self, statements: list[Stmt]) -> None:
        self._statements = statements

    def accept(self, visitor: Stmt.Visitor[R]) -> R:
        return visitor.visit_block_stmt(self)


class Class(Stmt):
    def __init__(self, name: Token, methods: list["Function"]) -> None:
        self._name = name
        self._methods = methods

    def accept(self, visitor: Stmt.Visitor[R]) -> R:
        return visitor.visit_class_stmt(self)


class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self._expression = expression

    def accept(self, visitor: Stmt.Visitor[R]) -> R:
        return visitor.visit_expression_stmt(self)


class Function(Stmt):
    def __init__(self, name: Token, params: list[Token], body: list[Stmt]) -> None:
        self._name = name
        self._params = params
        self._body = body

    def accept(self, visitor: Stmt.Visitor[R]) -> R:
        return visitor.visit_function_stmt(self)


class If(Stmt):
    def __init__(
        self, condition: Expr, then_branch: Stmt, else_branch: Stmt | None
    ) -> None:
        self._condition = condition
        self._then_branch = then_branch
        self._else_branch = else_branch

    def accept(self, visitor: Stmt.Visitor[R]) -> R:
        return visitor.visit_if_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self._expression = expression

    def accept(self, visitor: Stmt.Visitor[R]) -> R:
        return visitor.visit_print_stmt(self)


class Return(Stmt):
    def __init__(self, keyword: Token, value: Expr | None) -> None:
        self._keyword = keyword
        self._value = value

    def accept(self, visitor: Stmt.Visitor[R]) -> R:
        return visitor.visit_return_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr | None) -> None:
        self._name = name
        self._initializer = initializer

    def accept(self, visitor: Stmt.Visitor[R]) -> R:
        return visitor.visit_var_stmt(self)


class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt) -> None:
        self._condition = condition
        self._body = body

    def accept(self, visitor: Stmt.Visitor[R]) -> R:
        return visitor.visit_while_stmt(self)
