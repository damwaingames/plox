from math import isnan
from typing import Any

from abstract_syntax_tree import Expr, Binary, Grouping, Literal, Unary
from scanner.token import TokenType

class Interpreter:
    def evaluate(self, expression: Expr) -> Any:
        match expression:
            case Binary():
                left = self.evaluate(expression._left)
                right = self.evaluate(expression._right)
                match expression._operator.type:
                    case TokenType.BANG_EQUAL:
                        return not self._is_equal(left, right)
                    case TokenType.EQUAL_EQUAL:
                        return self._is_equal(left, right)
                    case TokenType.GREATER:
                        return float(left) > float(right)
                    case TokenType.GREATER_EQUAL:
                        return float(left) >= float(right)
                    case TokenType.LESS:
                        return float(left) < float(right)
                    case TokenType.LESS_EQUAL:
                        return float(left) <= float(right)
                    case TokenType.MINUS:
                        return float(left) - float(right)
                    case TokenType.PLUS:
                        if isinstance(left, float) and isinstance(right, float):
                            return float(left) + float(right)
                        if isinstance(left, str) and isinstance(right, str):
                            return str(left) + str(right)
                    case TokenType.SLASH:
                        try:
                            return float(left) / float(right)
                        except ZeroDivisionError:
                            return float("nan")
                    case TokenType.STAR:
                        return float(left) * float(right)
            case Grouping():
                return self.evaluate(expression._expression)
            case Literal():
                return expression._value
            case Unary():
                right = self.evaluate(expression._right)
                match expression._operator.type:
                    case TokenType.BANG:
                        return not self._is_truthy(right)
                    case TokenType.MINUS:
                        return -int(right)
            case _:
                raise NotImplementedError(f"Not added a case for a certain expression : {expression}")
    
    def _is_truthy(self, object: Any) -> bool:
        if object is None:
            return False
        if isinstance(object, bool):
            return object
        return True
    
    def _is_equal(self, a: Any, b: Any):
        if isinstance(a, float) and isinstance(b, float):
            # This is needed for the IEEE 754 non compliance of Lox
            if isnan(a) and isnan(b):
                return True
        return a == b if type(a) == type(b) else False