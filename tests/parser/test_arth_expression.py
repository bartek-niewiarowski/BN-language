import io
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.parser.parser import Parser
from interpreter.parser.syntax_error import *
from interpreter.parser.syntax_tree import *

class TestParseArthExpression:
    def test_single_term(self):
        parser = self._get_parser('42')
        result = parser.parse_arth_expression()
        assert isinstance(result, LiteralInt)
        assert result.value == 42

    def test_addition(self):
        parser = self._get_parser('3 + 4')
        result = parser.parse_arth_expression()
        assert isinstance(result, SumExpression)
        assert result.left.value == 3
        assert result.right.value == 4

    def test_subtraction(self):
        parser = self._get_parser('10 - 2')
        result = parser.parse_arth_expression()
        assert isinstance(result, SubExpression)
        assert result.left.value == 10
        assert result.right.value == 2

    def test_combined_addition_subtraction(self):
        parser = self._get_parser('4 + 3 - 2')
        result = parser.parse_arth_expression()
        assert isinstance(result, SubExpression)
        assert isinstance(result.left, SumExpression)
        assert result.left.left.value == 4
        assert result.left.right.value == 3
        assert result.right.value == 2

    def test_no_operators(self):
        parser = self._get_parser('x')
        result = parser.parse_arth_expression()
        assert isinstance(result, Identifier)
        assert result.name == 'x'

    def test_invalid_syntax_after_operator(self):
        parser = self._get_parser('x +')
        with pytest.raises(InvalidArthExpression):
            parser.parse_arth_expression()

    def test_complex_expression_with_parentheses(self):
        parser = self._get_parser('2 + (3 * 4)')
        result = parser.parse_arth_expression()
        assert isinstance(result, SumExpression)
        assert isinstance(result.right, MulExpression)
        assert result.right.left.value == 3
        assert result.right.right.value == 4

    def test_unexpected_token(self):
        parser = self._get_parser('2 + x * y')
        result = parser.parse_arth_expression()
        assert isinstance(result, SumExpression)
        assert isinstance(result.right, MulExpression)
        assert result.left.value == 2
        assert result.right.left.name == 'x'
        assert result.right.right.name == 'y'

    def test_mixed_variable_number_expression(self):
        parser = self._get_parser('x + 5')
        result = parser.parse_arth_expression()
        assert isinstance(result, SumExpression)
        assert isinstance(result.left, Identifier)
        assert result.left.name == 'x'
        assert result.right.value == 5

    def test_negative_numbers(self):
        parser = self._get_parser('-3 + 5')
        result = parser.parse_arth_expression()
        assert isinstance(result, SumExpression)
        assert isinstance(result.left, Negation)
        assert result.left.node.value == 3
        assert result.right.value == 5

    def test_operator_overloading(self):
        parser = self._get_parser('4 + + 3')
        with pytest.raises(InvalidArthExpression):
            parser.parse_arth_expression()
    
    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)
