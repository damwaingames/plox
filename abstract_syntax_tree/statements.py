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


class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self._expression = expression


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr) -> None:
        self._name = name
        self._initializer = initializer
