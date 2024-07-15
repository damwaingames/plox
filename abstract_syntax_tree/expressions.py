from abc import ABC
from typing import Any

from scanner.token import Token


class Expr(ABC):
    pass


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self._left = left
        self._right = right
        self._operator = operator


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr) -> None:
        self._operator = operator
        self._right = right


class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self._expression = expression


class Literal(Expr):
    def __init__(self, value: Any) -> None:
        self._value = value
