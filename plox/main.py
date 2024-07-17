import sys

import typer

from typing import Annotated

from abstract_syntax_tree import ASTPrinter
from errors import ErrorHandler
from interpreter import Interpreter
from parser import Parser
from scanner import Scanner


app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    plox: a lox interpreter written in python
    """


@app.command()
def tokenize(
    filename: Annotated[
        str, typer.Argument(help="File containing the lox script to be tokenized.")
    ],
) -> None:
    """
    Tokenize a lox script and display the results of the lexing pass.
    """
    tokens = get_tokens(filename)
    for token in tokens:
        print(token)
    if ErrorHandler.had_error:
        exit(65)


@app.command()
def parse(
    filename: Annotated[
        str, typer.Argument(help="File containing the lox script to be parsed.")
    ],
) -> None:
    """
    Parse a lox script and display the abstract syntax tree produced from the parsing pass.
    """
    tokens = get_tokens(filename)
    parser = Parser(tokens)
    statements = parser.parse()
    if ErrorHandler.had_error:
        exit(65)
    for statement in statements:
        print(ASTPrinter().print(statement))


@app.command()
def interpret(
    filename: Annotated[
        str, typer.Argument(help="File containing the lox script to be executed.")
    ],
) -> None:
    """
    Execute a lox script.
    """
    with open(filename) as file:
        file_contents = file.read()
    run(file_contents, Interpreter())
    if ErrorHandler.had_error:
        exit(65)
    if ErrorHandler.had_runtime_error:
        exit(70)


@app.command()
def repl() -> None:
    """
    Enter an interactive REPL for lox scripting.
    """
    interpreter = Interpreter()
    print("> ", end="", flush=True)
    for line in sys.stdin:
        run(line, interpreter)
        print("> ", end="", flush=True)
        ErrorHandler.had_error = False
        ErrorHandler.had_runtime_error = False


def run(source: str, interpreter: Interpreter) -> None:
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()
    if ErrorHandler.had_error:
        return
    interpreter.interpret(statements)


def get_tokens(filename):
    with open(filename) as file:
        file_contents = file.read()
    tokens = Scanner(file_contents).scan_tokens()
    return tokens
