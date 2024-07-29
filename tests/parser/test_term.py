import io
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.parser.parser import Parser
from interpreter.parser.syntax_error import *
from interpreter.parser.syntax_tree import *

class TestParseTerm:
    def test_single_factor(self):
        parser = self._get_parser('42')
        result = parser.parse_term()
        assert isinstance(result, LiteralInt)
        assert result.value == 42

    def test_multiplication(self):
        parser = self._get_parser('3 * 4')
        result = parser.parse_term()
        assert isinstance(result, MulExpression)
        assert result.left.value == 3
        assert result.right.value == 4

    def test_division(self):
        parser = self._get_parser('10 / 2')
        result = parser.parse_term()
        assert isinstance(result, DivExpression)
        assert result.left.value == 10
        assert result.right.value == 2

    def test_combined_multiplication_division(self):
        parser = self._get_parser('4 * 3 / 2')
        result = parser.parse_term()
        assert isinstance(result, DivExpression)
        assert isinstance(result.left, MulExpression)
        assert result.left.left.value == 4
        assert result.left.right.value == 3
        assert result.right.value == 2

    def test_no_operators(self):
        parser = self._get_parser('x')
        result = parser.parse_term()
        assert isinstance(result, Identifier)
        assert result.name == 'x'

    def test_invalid_syntax_after_operator(self):
        parser = self._get_parser('x *')
        with pytest.raises(InvalidTerm):
            parser.parse_term()

    def test_division_by_zero_static(self):
        parser = self._get_parser('x / 0')
        result = parser.parse_term()
        assert isinstance(result, DivExpression)
        assert isinstance(result.left, Identifier)
        assert result.left.name == 'x'
        assert result.right.value == 0

    def test_chained_multiplications(self):
        parser = self._get_parser('2 * 2 * 2')
        result = parser.parse_term()
        assert isinstance(result, MulExpression)
        assert isinstance(result.left, MulExpression)
        assert result.left.left.value == 2
        assert result.left.right.value == 2
        assert result.right.value == 2

    def test_complex_expression(self):
        parser = self._get_parser('2 * (3 + 4)')
        result = parser.parse_term()
        assert isinstance(result, MulExpression)
        assert result.left.value == 2
        assert isinstance(result.right, SumExpression)
        assert result.right.left.value == 3
        assert result.right.right.value == 4

    def test_nested_parentheses(self):
        parser = self._get_parser('((3 + 2) * (1 + 1))')
        result = parser.parse_arth_expression()
        assert isinstance(result, MulExpression)
        assert isinstance(result.left, SumExpression)
        assert result.left.left.value == 3
        assert result.left.right.value == 2
        assert isinstance(result.right, SumExpression)
        assert result.right.left.value == 1
        assert result.right.right.value == 1
    
    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)

