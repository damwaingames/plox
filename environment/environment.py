from typing import Any

from errors import LoxRuntimeError
from scanner.token import Token


class Environment:
    def __init__(self) -> None:
        self._values: dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self._values.update({name: value})

    def get(self, name: Token) -> Any:
        val = self._values.get(name.lexeme)
        if val:
            return val
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self._values:
            self._values.update({name.lexeme: value})
            return
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")