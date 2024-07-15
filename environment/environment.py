from typing import Any, Optional

from errors import LoxRuntimeError
from scanner.token import Token


class Environment:
    def __init__(self, enclosing: Optional["Environment"] = None) -> None:
        self._values: dict[str, Any] = {}
        self._enclosing = enclosing

    def define(self, name: str, value: Any) -> None:
        self._values.update({name: value})

    def get(self, name: Token) -> Any:
        val = self._values.get(name.lexeme)
        if val:
            return val
        if self._enclosing:
            return self._enclosing.get(name)
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self._values:
            self._values.update({name.lexeme: value})
            return
        if self._enclosing:
            self._enclosing.assign(name, value)
            return
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
