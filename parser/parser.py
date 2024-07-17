from errors import ErrorHandler, LoxParseError
from scanner.token import Token, TokenType
from abstract_syntax_tree.expressions import (
    Expr,
    Assign,
    Binary,
    Call,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from abstract_syntax_tree.statements import (
    Stmt,
    Block,
    Expression,
    Function,
    If,
    Print,
    Var,
    While,
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

    def _finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    ErrorHandler.error(
                        self._peek(), "Can't have more than 255 arguments."
                    )
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        paren = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def _call(self) -> Expr:
        expression = self._primary()
        while True:
            if self._match(TokenType.LEFT_PAREN):
                expression = self._finish_call(expression)
            else:
                break
        return expression

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)
        return self._call()

    def _factor(self) -> Expr:
        expression = self._unary()
        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._unary()
            expression = Binary(expression, operator, right)
        return expression

    def _term(self) -> Expr:
        expression = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            right = self._factor()
            expression = Binary(expression, operator, right)
        return expression

    def _comparison(self) -> Expr:
        expression = self._term()
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
        expression = self._comparison()
        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expression = Binary(expression, operator, right)
        return expression

    def _and(self) -> Expr:
        expression = self._equality()
        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expression = Logical(expression, operator, right)
        return expression

    def _or(self) -> Expr:
        expression = self._and()
        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._and()
            expression = Logical(expression, operator, right)
        return expression

    def _assignment(self) -> Expr:
        expression = self._or()
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
        else:
            initializer = None
        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def _while_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after 'while' condition.")
        body = self._statement()
        return While(condition, body)

    def _function(self, kind: str) -> Function:
        name = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters: list[Token] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    ErrorHandler.error(
                        self._peek(), "Can't have more than 255 parameters."
                    )
                parameters.append(
                    self._consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self._consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self._block()
        return Function(name, parameters, body)

    def _expression_statement(self) -> Stmt:
        expression = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expression)

    def _block(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            x = self._declaration()
            if x:
                statements.append(x)
        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def _if_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after 'if' condition.")
        then_branch = self._statement()
        else_branch = self._statement() if self._match(TokenType.ELSE) else None
        return If(condition, then_branch, else_branch)

    def _for_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after 'for' condition.")

        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after 'for' clauses.")

        body = self._statement()

        if increment is not None:
            body = Block([body, Expression(increment)])
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)
        if initializer is not None:
            body = Block([initializer, body])
        return body

    def _statement(self) -> Stmt:
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.PRINT):
            return self._print_statment()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.LEFT_BRACE):
            return Block(self._block())
        return self._expression_statement()

    def _declaration(self) -> Stmt | None:
        try:
            if self._match(TokenType.FUN):
                return self._function("function")
            if self._match(TokenType.VAR):
                return self._var_declaration()
            return self._statement()
        except LoxParseError:
            self._synchronize()
            return None
