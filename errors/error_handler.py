import sys

from typing import assert_never

from scanner.token import Token, TokenType


class ErrorHandler:
    had_error = False

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        ErrorHandler.had_error = True

    @staticmethod
    def error(identifier: int | Token, message: str) -> None:
        match identifier:
            case int():
                ErrorHandler.report(identifier, "", message)
            case Token():
                where = (
                    " at end"
                    if identifier.type == TokenType.EOF
                    else f" a '{identifier.lexeme}'"
                )
                ErrorHandler.report(identifier.line, where, message)
            case _:
                assert_never(identifier)
