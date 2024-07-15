from .expressions import Expr, Binary, Unary, Grouping, Literal
from .statements import Stmt, Expression, Print


class ASTPrinter:
    def print_stmt(self, statement: Stmt) -> str:
        match statement:
            case Expression():
                return self._parenthesize(";", statement._expression)
            case Print():
                return self._parenthesize("print", statement._expression)
            case _:
                raise NotImplementedError(
                    f"Not added a case for a certain statement : {statement}"
                )

    def print_expr(self, expression: Expr) -> str:
        match expression:
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
            case _:
                raise NotImplementedError(
                    f"Not added a case for a certain expression : {expression}"
                )

    def _parenthesize(self, name: str, *args: Expr) -> str:
        output = f"({name}"
        for expression in args:
            output += " "
            match expression:
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
                case _:
                    raise NotImplementedError(
                        f"Not added a case for a certain expression : {expression}"
                    )
        output += ")"
        return output
