from abc import ABC

from .expressions import Expr


class Stmt(ABC):
    pass


class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self._expression = expression


class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self._expression = expression
