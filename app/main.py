import sys

from abstract_syntax_tree import ASTPrinter, Expr
from errors import ErrorHandler, LoxParseError
from interpreter import Interpreter
from parser import Parser
from scanner import Scanner
from scanner.token import Token


def tokenize(filename: str) -> list[Token]:
    with open(filename) as file:
        file_contents = file.read()
    tokens = Scanner(file_contents).scan_tokens()
    return tokens


def parse(tokens: list[Token]) -> Expr:
    parser = Parser(tokens)
    expression = parser.parse()
    if ErrorHandler.had_error:
        raise LoxParseError()
    if expression:
        return expression
    raise LoxParseError()


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    match command:
        case "tokenize":
            for token in tokenize(filename):
                print(token)
        case "parse":
            try:
                expression = parse(tokenize(filename))
                print(ASTPrinter().print(expression))
            except LoxParseError:
                pass
        case "interpret":
            interpreter = Interpreter()
            interpreter.interpret(parse(tokenize(filename)))

        case _:
            print(f"Unknown command: {command}", file=sys.stderr)
            exit(1)

    if ErrorHandler.had_error:
        exit(65)
    if ErrorHandler.had_runtime_error:
        exit(70)


if __name__ == "__main__":
    main()
