from typing import Any

from .expressions import (
    Expr,
    Assign,
    Binary,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from .statements import Stmt, Block, Expression, If, Print, Var, While
from scanner.token import Token


class ASTPrinter(Expr.Visitor, Stmt.Visitor):
    def print(self, x: Expr | Stmt) -> str:
        return x.accept(self)

    def visit_block_stmt(self, stmt: Block) -> Any:
        builder = "(block "
        for statement in stmt._statements:
            builder += statement.accept(self)
        builder += ")"
        return builder

    def visit_expression_stmt(self, stmt: Expression) -> Any:
        return self._parenthesize(";", stmt._expression)

    def visit_if_stmt(self, stmt: If) -> Any:
        if stmt._else_branch is None:
            return self._parenthesize2("if", stmt._condition, stmt._then_branch)
        return self._parenthesize2(
            "if-else", stmt._condition, stmt._then_branch, stmt._else_branch
        )

    def visit_print_stmt(self, stmt: Print) -> Any:
        return self._parenthesize("print", stmt._expression)

    def visit_var_stmt(self, stmt: Var) -> Any:
        if stmt._initializer is None:
            return self._parenthesize2("var", stmt._name)
        return self._parenthesize2("var", stmt._name, "=", stmt._initializer)

    def visit_while_stmt(self, stmt: While) -> Any:
        return self._parenthesize2("while", stmt._condition, stmt._body)

    def visit_assign_expr(self, expr: Assign) -> Any:
        return self._parenthesize2("=", expr._name.lexeme, expr._value)

    def visit_binary_expr(self, expr: Binary) -> Any:
        return self._parenthesize(expr._operator.lexeme, expr._left, expr._right)

    def visit_grouping_expr(self, expr: Grouping) -> Any:
        return self._parenthesize("group", expr._expression)

    def visit_literal_expr(self, expr: Literal) -> Any:
        return "nil" if expr._value is None else str(expr._value)

    def visit_logical_expr(self, expr: Logical) -> Any:
        return self._parenthesize(expr._operator.lexeme, expr._left, expr._right)

    def visit_unary_expr(self, expr: Unary) -> Any:
        return self._parenthesize(expr._operator.lexeme, expr._right)

    def visit_variable_expr(self, expr: Variable) -> Any:
        return expr._name.lexeme

    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        builder = f"({name}"
        for expr in exprs:
            builder += " "
            builder += expr.accept(self)
        builder += ")"
        return builder

    def _parenthesize2(self, name: str, *parts: Any) -> str:
        builder = f"({name}"
        builder = self._transform(builder, parts)
        builder += ")"
        return builder

    def _transform(self, builder: str, *parts: Any) -> str:
        for part in parts:
            builder += " "
            match part:
                case Expr() | Stmt():
                    builder += part.accept(self)
                case Token():
                    builder += part.lexeme
                case tuple():
                    builder += self._transform(builder, *part)
                case _:
                    builder += part
        return builder
