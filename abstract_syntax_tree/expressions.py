from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from scanner.token import Token

R = TypeVar("R")


class Expr(ABC):
    class Visitor(ABC, Generic[R]):
        @abstractmethod
        def visit_assign_expr(self, expr: "Assign") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_binary_expr(self, expr: "Binary") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_grouping_expr(self, expr: "Grouping") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_literal_expr(self, expr: "Literal") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_logical_expr(self, expr: "Logical") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_unary_expr(self, expr: "Unary") -> R:
            raise NotImplementedError()

        @abstractmethod
        def visit_variable_expr(self, expr: "Variable") -> R:
            raise NotImplementedError()

    @abstractmethod
    def accept(self, visitor: Visitor[R]) -> R:
        raise NotImplementedError()


class Assign(Expr):
    def __init__(self, name: Token, value: Expr) -> None:
        self._name = name
        self._value = value

    def accept(self, visitor: Expr.Visitor[R]) -> R:
        return visitor.visit_assign_expr(self)


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self._left = left
        self._right = right
        self._operator = operator

    def accept(self, visitor: Expr.Visitor[R]) -> R:
        return visitor.visit_binary_expr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self._expression = expression

    def accept(self, visitor: Expr.Visitor[R]) -> R:
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self, value: Any) -> None:
        self._value = value

    def accept(self, visitor: Expr.Visitor[R]) -> R:
        return visitor.visit_literal_expr(self)


class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self._left = left
        self._right = right
        self._operator = operator

    def accept(self, visitor: Expr.Visitor[R]) -> R:
        return visitor.visit_logical_expr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr) -> None:
        self._operator = operator
        self._right = right

    def accept(self, visitor: Expr.Visitor[R]) -> R:
        return visitor.visit_unary_expr(self)


class Variable(Expr):
    def __init__(self, name: Token) -> None:
        self._name = name

    def accept(self, visitor: Expr.Visitor[R]) -> R:
        return visitor.visit_variable_expr(self)
