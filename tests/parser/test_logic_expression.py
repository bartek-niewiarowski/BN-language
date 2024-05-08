import io
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.parser.parser import Parser
from interpreter.parser.syntax_error import *
from interpreter.parser.syntax_tree import *

class TestParseLogicExpression:
    def test_single_arithmetic_expression(self):
        parser = self._get_parser('42')
        result = parser.parse_logic_expression()
        assert hasattr(result, 'value') and result.value == 42

    def test_logic_expression_with_equal_operator(self):
        parser = self._get_parser('x == y')
        result = parser.parse_logic_expression()
        pass
        assert hasattr(result, 'left') and hasattr(result.left, 'name')
        assert hasattr(result, 'right') and hasattr(result.right, 'name')

    def test_logic_expression_with_greater_than_operator(self):
        parser = self._get_parser('x > y')
        result = parser.parse_logic_expression()
        assert hasattr(result, 'left') and hasattr(result.left, 'name')
        assert hasattr(result, 'right') and hasattr(result.right, 'name')

    def test_logic_expression_with_multiple_operators(self):
        # Assuming only the first operator is parsed by `parse_logic_expression`
        parser = self._get_parser('x < y == z')
        result = parser.parse_logic_expression()
        assert hasattr(result, 'left') and hasattr(result.left, 'name')
        assert hasattr(result, 'right') and hasattr(result.right, 'name')

    def test_missing_right_expression(self):
        parser = self._get_parser('x <')
        with pytest.raises(InvalidLogicExpression):
            parser.parse_logic_expression()

    def test_invalid_right_expression(self):
        parser = self._get_parser('x < +')
        with pytest.raises(InvalidLogicExpression):
            parser.parse_logic_expression()

    def test_complex_arithmetic_expression(self):
        parser = self._get_parser('3 + 4 > 2')
        result = parser.parse_logic_expression()
        assert hasattr(result, 'left')
        assert hasattr(result, 'right') and hasattr(result.right, 'value')

    def test_logic_expression_with_not_equal_operator(self):
        parser = self._get_parser('x != y')
        result = parser.parse_logic_expression()
        assert hasattr(result, 'left') and hasattr(result, 'right')
        assert isinstance(result, NotEqualOperation)

    def test_boolean_values_comparison(self):
        parser = self._get_parser('true == false')
        result = parser.parse_logic_expression()
        assert hasattr(result, 'left') and hasattr(result, 'right')
        assert isinstance(result, EqualOperation)

    def test_arithmetic_and_logic_combination(self):
        parser = self._get_parser('sum(x, y) > avg(a, b)')
        result = parser.parse_logic_expression()
        assert hasattr(result, 'left') and hasattr(result, 'right')
        assert isinstance(result.left, FunctionCall) and isinstance(result.right, FunctionCall)
    
    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)