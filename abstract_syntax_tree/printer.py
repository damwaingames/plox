from typing import Any

from .expressions import (
    Expr,
    Assign,
    Binary,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from .statements import Stmt, Block, Expression, If, Print, Var
from scanner.token import Token


class ASTPrinter:
    def print_stmt(self, statement: Stmt) -> str:
        match statement:
            case Block():
                return self._parenthesize2("block", *statement._statements)
            case Expression():
                return self._parenthesize(";", statement._expression)
            case If():
                if statement._else_branch:
                    return self._parenthesize2(
                        "if-else",
                        statement._condition,
                        statement._then_branch,
                        statement._else_branch,
                    )
                return self._parenthesize2(
                    "if", statement._condition, statement._then_branch
                )
            case Print():
                return self._parenthesize("print", statement._expression)
            case Var():
                if statement._initializer is None:
                    return self._parenthesize2("var", statement._name)
                return self._parenthesize2(
                    "var", statement._name, "=", statement._initializer
                )
            case _:
                raise NotImplementedError(
                    f"Not added a case for a certain statement : {statement}"
                )

    def print_expr(self, expression: Expr) -> str:
        match expression:
            case Assign():
                return self._parenthesize2(expression._name.lexeme, expression._value)
            case Binary():
                return self._parenthesize(
                    expression._operator.lexeme, expression._left, expression._right
                )
            case Grouping():
                return self._parenthesize("group", expression._expression)
            case Literal():
                match expression._value:
                    case None:
                        return "nil"
                    case bool():
                        return str(expression._value).lower()
                    case _:
                        return str(expression._value)
            case Logical():
                return self._parenthesize(
                    expression._operator.lexeme, expression._left, expression._right
                )
            case Unary():
                return self._parenthesize(
                    expression._operator.lexeme, expression._right
                )
            case Variable():
                return expression._name.lexeme
            case _:
                raise NotImplementedError(
                    f"Not added a case for a certain expression : {expression}"
                )

    def _parenthesize(self, name: str, *args: Expr) -> str:
        output = f"({name}"
        for expression in args:
            output += " "
            output += self.print_expr(expression)
        output += ")"
        return output

    def _parenthesize2(self, name: str, *parts: Any) -> str:
        output = f"({name}"
        output = self._transform(output, parts)
        output += ")"
        return output

    def _transform(self, output: str, *parts: Any) -> str:
        for part in parts:
            output += " "
            match part:
                case Expr():
                    output += self.print_expr(part)
                case Stmt():
                    output += self.print_stmt(part)
                case Token():
                    output += part.lexeme
                case tuple():
                    output += self._transform(output, *part)
                case str():
                    output += part
                case _:
                    raise NotImplementedError(
                        f"Not added a case for a certain expression or statement : {part}"
                    )
        return output
