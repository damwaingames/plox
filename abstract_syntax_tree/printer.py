from typing import Any

from .expressions import Expr, Assign, Binary, Grouping, Literal, Unary, Variable
from .statements import Stmt, Expression, Print, Var
from scanner.token import Token


class ASTPrinter:
    def print_stmt(self, statement: Stmt) -> str:
        match statement:
            case Expression():
                return self._parenthesize(";", statement._expression)
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
            match expression:
                case Assign():
                    output += self._parenthesize2(
                        "=", expression._name.lexeme, expression._value
                    )
                case Binary():
                    output += self._parenthesize(
                        expression._operator.lexeme, expression._left, expression._right
                    )
                case Grouping():
                    output += self._parenthesize("group", expression._expression)
                case Literal():
                    match expression._value:
                        case None:
                            output += "nil"
                        case bool():
                            output += str(expression._value).lower()
                        case _:
                            output += str(expression._value)
                case Unary():
                    output += self._parenthesize(
                        expression._operator.lexeme, expression._right
                    )
                case Variable():
                    output += expression._name.lexeme
                case _:
                    raise NotImplementedError(
                        f"Not added a case for a certain expression : {expression}"
                    )
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
                case Assign():
                    output += self._parenthesize2("=", part._name.lexeme, part._value)
                case Binary():
                    output += self._parenthesize(
                        part._operator.lexeme, part._left, part._right
                    )
                case Grouping():
                    output += self._parenthesize("group", part._expression)
                case Literal():
                    match part._value:
                        case None:
                            output += "nil"
                        case bool():
                            output += str(part._value).lower()
                        case _:
                            output += str(part._value)
                case Unary():
                    output += self._parenthesize(part._operator.lexeme, part._right)
                case Variable():
                    output += part._name.lexeme
                case Expression():
                    output += self._parenthesize(";", part._expression)
                case Print():
                    output += self._parenthesize("print", part._expression)
                case Var():
                    if part._initializer is None:
                        output += self._parenthesize2("var", part._name)
                    else:
                        output += self._parenthesize2(
                            "var", part._name, "=", part._initializer
                        )
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
