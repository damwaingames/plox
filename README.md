# `plox`
This is a python implemenation of the lox langauge as described in the book [Crafting Interpreters](https://craftinginterpreters.com/) by Robert Nystrom. In particular the first version from part 2.

## Current state
- Line comments implemented (`// comment`)
- Expressions implemented
  - [x] Assignment (`IDENTIFIER = Expr`)
  - [x] Binary
    - [x] Addition or Concatenation (`Expr + Expr`)
    - [x] Subtraction (`Expr - Expr`)
    - [x] Multiplication (`Expr * Expr`)
    - [x] Division (`Expr / Expr`)
    - [x] Comparisons
      - [x] Equality (`Expr == Expr`)
      - [x] Inequality (`Expr != Expr`)
      - [x] Greater (`Expr > Expr`)
      - [x] Greater or Equal (`Expr >= Expr`)
      - [x] Less (`Expr < Expr`)
      - [x] Less or Equal (`Expr <= Expr`)
  - [ ] Call (`IDENTIFIER()`)
  - [ ] Get (`IDENTIFIER.IDENTIFIER`)
  - [x] Groupings (`(Expr)`)
  - [x] Literals (`NUMBER`, `STRING`, `IDENTIFIER`, `true`, `false`, `"nil"`)
  - [ ] Logical
    - [ ] And (`Expr and Expr`)
    - [ ] Or (`Expr or Expr`)
  - [ ] Set (`Expr = Expr`)
  - [ ] Super (`super.IDENTIFIER`)
  - [ ] This (`this.IDENTIFIER`)
  - [x] Unary
    - [x] Negation (`-Expr`)
    - [x] Logical Inverse (`!Expr`)
  - [x] Variable (`IDENTIFIER`)
- Statements implemented
  - [x] Block (`{Stmt}`)
  - [ ] Class (`class IDENTIFIER {Stmt}`)
  - [x] Expression (`Expr;`)
  - [ ] Function (`fun IDENTIFIER {Stmt}`)
  - [ ] If (`if (Expr) {Stmt} else {Stmt}`)
  - [x] Print (`print Expr;`)
  - [ ] Return (`return Expr;`)
  - [x] Var (`var IDENTIFIER;`)
  - [ ] While (`while (Expr) {Stmt}`)
- Scopes implemented
    [x] Global
    [x] Block


## Usage

plox: a lox interpreter written in python

**Usage**:

```console
$ plox [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `interpret`: Execute a lox script.
* `parse`: Parse a lox script and display the...
* `repl`: Enter an interactive REPL for lox scripting.
* `tokenize`: Tokenize a lox script and display the...

## `plox interpret`

Execute a lox script.

**Usage**:

```console
$ plox interpret [OPTIONS] FILENAME
```

**Arguments**:

* `FILENAME`: File containing the lox script to be executed.  [required]

**Options**:

* `--help`: Show this message and exit.

## `plox parse`

Parse a lox script and display the abstract syntax tree produced from the parsing pass.

**Usage**:

```console
$ plox parse [OPTIONS] FILENAME
```

**Arguments**:

* `FILENAME`: File containing the lox script to be parsed.  [required]

**Options**:

* `--help`: Show this message and exit.

## `plox repl`

Enter an interactive REPL for lox scripting.

**Usage**:

```console
$ plox repl [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `plox tokenize`

Tokenize a lox script and display the results of the lexing pass.

**Usage**:

```console
$ plox tokenize [OPTIONS] FILENAME
```

**Arguments**:

* `FILENAME`: File containing the lox script to be tokenized.  [required]

**Options**:

* `--help`: Show this message and exit.
