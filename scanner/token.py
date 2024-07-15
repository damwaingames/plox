from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    # Single-character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    BANG = auto()
    EQUAL = auto()
    GREATER = auto()
    LESS = auto()

    # Two character tokens
    BANG_EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()

    # Other
    EOF = auto()


class Token:
    def __init__(
        self,
        t_type: TokenType,
        lexeme: str,
        literal: Any,
        line: int,
    ) -> None:
        self.type = t_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self) -> str:
        return f"{str(self.type).split(".")[-1]} {self.lexeme} {self.literal if self.literal is not None else "null"}"
