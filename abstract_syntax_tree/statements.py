from abc import ABC

from scanner.token import Token

from .expressions import Expr


class Stmt(ABC):
    pass


class Block(Stmt):
    def __init__(self, statements: list[Stmt]) -> None:
        self._statements = statements


class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self._expression = expression


class If(Stmt):
    def __init__(
        self, condition: Expr, then_branch: Stmt, else_branch: Stmt | None = None
    ) -> None:
        self._condition = condition
        self._then_branch = then_branch
        self._else_branch = else_branch


class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self._expression = expression


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr) -> None:
        self._name = name
        self._initializer = initializer
