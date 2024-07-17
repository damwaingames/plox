from abc import ABC, abstractmethod
from time import time
from typing import Any, TYPE_CHECKING

from abstract_syntax_tree.statements import Function
from environment import Environment
from errors import LoxReturn

if TYPE_CHECKING:
    from interpreter import Interpreter


class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        raise NotImplementedError()


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
