from typing import Any

from errors import ErrorHandler

from .token import Token, TokenType


class Scanner:
    keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def __init__(self, source: str) -> None:
        self._source = source
        self._tokens: list[Token] = []
        self._start = 0
        self._current = 0
        self._line = 1

    def _is_at_end(self) -> bool:
        return self._current >= len(self._source)

    def _advance(self) -> str:
        next_char = self._source[self._current]
        self._current += 1
        return next_char

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        check = self._source[self._current] == expected
        if check:
            self._current += 1
        return check

    def _peek(self) -> str:
        return "\0" if self._is_at_end() else self._source[self._current]

    def _peek_next(self) -> str:
        return (
            "\0"
            if self._current + 1 >= len(self._source)
            else self._source[self._current + 1]
        )

    def _add_token(self, t_type: TokenType, literal: Any | None = None) -> None:
        text = self._source[self._start : self._current]
        self._tokens.append(Token(t_type, text, literal, self._line))

    def _string(self) -> None:
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self._line += 1
            self._advance()
        if self._is_at_end():
            ErrorHandler.error(self._line, "Unterminated string.")
            return
        self._advance()
        self._add_token(
            TokenType.STRING, self._source[self._start + 1 : self._current - 1]
        )

    def _is_digit(self, char: str) -> bool:
        return char in [str(x) for x in range(10)]

    def _number(self) -> None:
        while self._is_digit(self._peek()):
            self._advance()
        if self._peek() == "." and self._is_digit(self._peek_next()):
            self._advance()
            while self._is_digit(self._peek()):
                self._advance()
        self._add_token(
            TokenType.NUMBER, float(self._source[self._start : self._current])
        )

    def _is_alpha(self, char) -> bool:
        return char.isalpha() or char == "_"

    def _is_alphanumeric(self, char) -> bool:
        return self._is_digit(char) or self._is_alpha(char)

    def _identifier(self):
        while self._is_alphanumeric(self._peek()):
            self._advance()
        t_type = Scanner.keywords.get(self._source[self._start : self._current])
        if not t_type:
            t_type = TokenType.IDENTIFIER
        self._add_token(t_type)

    def scan_tokens(self) -> list[Token]:
        while not self._is_at_end():
            self._start = self._current
            self.scan_token()
        self._tokens.append(Token(TokenType.EOF, "", None, self._line))
        return self._tokens

    def scan_token(self) -> None:
        char = self._advance()
        match char:
            # Single-character tokens
            case "(":
                self._add_token(TokenType.LEFT_PAREN)
            case ")":
                self._add_token(TokenType.RIGHT_PAREN)
            case "{":
                self._add_token(TokenType.LEFT_BRACE)
            case "}":
                self._add_token(TokenType.RIGHT_BRACE)
            case ",":
                self._add_token(TokenType.COMMA)
            case ".":
                self._add_token(TokenType.DOT)
            case "-":
                self._add_token(TokenType.MINUS)
            case "+":
                self._add_token(TokenType.PLUS)
            case ";":
                self._add_token(TokenType.SEMICOLON)
            case "*":
                self._add_token(TokenType.STAR)
            # One or two character tokens
            case "!":
                self._add_token(
                    TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG
                )
            case "=":
                self._add_token(
                    TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
                )
            case ">":
                self._add_token(
                    TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
                )
            case "<":
                self._add_token(
                    TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
                )
            # Comment check special case
            case "/":
                if self._match("/"):
                    while self._peek() != "\n" and not self._is_at_end():
                        self._advance()
                else:
                    self._add_token(TokenType.SLASH)
            # Ignore whitespace
            case " " | "\t" | "\r":
                pass
            # New line - increment line count
            case "\n":
                self._line += 1
            # String Literals
            case '"':
                self._string()
            case _:
                # Number literals
                if self._is_digit(char):
                    self._number()
                # Identifier literals and keywords
                elif self._is_alpha(char):
                    self._identifier()
                # Anythin else
                else:
                    ErrorHandler.error(self._line, f"Unexpected character: {char}")
