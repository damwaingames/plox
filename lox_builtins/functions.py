from abc import ABC, abstractmethod
from time import time
from typing import Any, TYPE_CHECKING, Union

from abstract_syntax_tree.statements import Function
from environment import Environment
from errors import LoxReturn, LoxRuntimeError
from scanner.token import Token

if TYPE_CHECKING:
    from interpreter import Interpreter


class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        raise NotImplementedError()


class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: dict[str, "LoxFunction"]) -> None:
        self.name = name
        self._methods = methods

    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        instance = LoxInstance(self)
        return instance

    def arity(self) -> int:
        return 0

    def find_method(self, name: str) -> Union["LoxFunction", None]:
        if name in self._methods.keys():
            return self._methods.get(name)
        return None

    def __repr__(self) -> str:
        return self.name


class LoxInstance:
    def __init__(self, klass: LoxClass) -> None:
        self._klass = klass
        self._fields: dict[str, Any] = {}

    def get(self, name: Token) -> Any:
        if name.lexeme in self._fields.keys():
            return self._fields.get(name.lexeme)
        method = self._klass.find_method(name.lexeme)
        if method:
            return method
        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any) -> None:
        self._fields.update({name.lexeme: value})

    def __repr__(self) -> str:
        return f"{self._klass.name} instance"


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment) -> None:
        self._declaration = declaration
        self._closure = closure

    def arity(self) -> int:
        return len(self._declaration._params)

    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        environment = Environment(self._closure)
        for i, param in enumerate(self._declaration._params):
            environment.define(param.lexeme, arguments[i])
        try:
            interpreter.execute_block(self._declaration._body, environment)
        except LoxReturn as rtn_val:
            return rtn_val.args[0]
        return None

    def __repr__(self) -> str:
        return f"<fn {self._declaration._name.lexeme}>"


class ClockFunction(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        return time()

    def __repr__(self) -> str:
        return "<native fn>"
