from abc import ABC
from typing import Any

from scanner.token import Token


class Expr(ABC):
    pass


class Assign(Expr):
    def __init__(self, name: Token, value: Expr) -> None:
        self._name = name
        self._value = value


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


class Variable(Expr):
    def __init__(self, name: Token) -> None:
        self._name = name
