from typing import Any, Optional

from errors import LoxRuntimeError
from scanner.token import Token


class Environment:
    def __init__(self, enclosing: Optional["Environment"]) -> None:
        self._values: dict[str, Any] = {}
        self._enclosing = enclosing

    def get(self, name: Token) -> Any:
        if name.lexeme in self._values.keys():
            return self._values[name.lexeme]
        if self._enclosing is not None:
            return self._enclosing.get(name)
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self._values.keys():
            self._values.update({name.lexeme: value})
            return
        if self._enclosing is not None:
            self._enclosing.assign(name, value)
            return
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def define(self, name: str, value: Any) -> None:
        self._values.update({name: value})

    def __repr__(self) -> str:
        return f"values: {self._values}\nenclosing environment: {self._enclosing}"
