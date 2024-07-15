from errors import ErrorHandler, LoxParseError
from scanner.token import Token, TokenType
from abstract_syntax_tree import (
    Expr,
    Assign,
    Binary,
    Grouping,
    Literal,
    Unary,
    Variable,
    Stmt,
    Expression,
    Print,
    Var,
)


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._current = 0

    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self._is_at_end():
            x = self._declaration()
            if x:
                statements.append(x)
        return statements

    def _peek(self) -> Token:
        return self._tokens[self._current]

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _previous(self) -> Token:
        return self._tokens[self._current - 1]

    def _advance(self) -> Token:
        if not self._is_at_end():
            self._current += 1
        return self._previous()

    def _check(self, t_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == t_type

    def _match(self, *args: TokenType) -> bool:
        for t_type in args:
            if self._check(t_type):
                self._advance()
                return True
        return False

    def _error(self, token: Token, message: str) -> LoxParseError:
        ErrorHandler.error(token, message)
        return LoxParseError()

    def _consume(self, t_type: TokenType, message: str) -> Token:
        if self._check(t_type):
            return self._advance()
        raise self._error(self._peek(), message)

    def _synchronize(self) -> None:
        self._advance()
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            match self._peek().type:
                case (
                    TokenType.CLASS
                    | TokenType.FOR
                    | TokenType.FUN
                    | TokenType.IF
                    | TokenType.PRINT
                    | TokenType.RETURN
                    | TokenType.VAR
                    | TokenType.WHILE
                ):
                    return
            self._advance()

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return Literal(False)
        if self._match(TokenType.TRUE):
            return Literal(True)
        if self._match(TokenType.NIL):
            return Literal(None)
        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)
        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())
        if self._match(TokenType.LEFT_PAREN):
            expression = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expression)
        raise self._error(self._peek(), "Expect expression.")

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)
        return self._primary()

    def _factor(self) -> Expr:
        expression: Expr = self._unary()
        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._unary()
            expression = Binary(expression, operator, right)
        return expression

    def _term(self) -> Expr:
        expression: Expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            right = self._factor()
            expression = Binary(expression, operator, right)
        return expression

    def _comparison(self) -> Expr:
        expression: Expr = self._term()
        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self._previous()
            right = self._term()
            expression = Binary(expression, operator, right)
        return expression

    def _equality(self) -> Expr:
        expression: Expr = self._comparison()
        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expression = Binary(expression, operator, right)
        return expression

    def _assignment(self) -> Expr:
        expression = self._equality()
        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()
            if isinstance(expression, Variable):
                name = expression._name
                return Assign(name, value)
            ErrorHandler.error(equals, "Invalid assignment target.")
        return expression

    def _expression(self) -> Expr:
        return self._assignment()

    def _print_statment(self) -> Stmt:
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def _var_declaration(self) -> Stmt:
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        if self._match(TokenType.EQUAL):
            initializer = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def _expression_statement(self) -> Stmt:
        expression = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expression)

    def _statement(self) -> Stmt:
        if self._match(TokenType.PRINT):
            return self._print_statment()
        return self._expression_statement()

    def _declaration(self) -> Stmt | None:
        try:
            if self._match(TokenType.VAR):
                return self._var_declaration()
            return self._statement()
        except LoxParseError:
            self._synchronize()
            return None
