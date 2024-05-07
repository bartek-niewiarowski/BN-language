import io
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.tokens.token import Token
from interpreter.tokens.token_type import TokenType
from interpreter.lexer.error import LexerError
from interpreter.source.source_position import SourcePosition
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
        assert result[0].value == 3
        assert result[1].nodes.value == 4

    def test_division(self):
        parser = self._get_parser('10 / 2')
        result = parser.parse_term()
        assert result[0].value == 10
        assert result[1].nodes.value == 2

    def test_combined_multiplication_division(self):
        parser = self._get_parser('4 * 3 / 2')
        result = parser.parse_term()
        assert result[0].value == 4
        assert result[1].nodes.value == 3
        assert result[2].nodes.value == 2

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
        assert result[0].name == 'x'
        assert result[1].nodes.value == 0

    def test_chained_multiplications(self):
        parser = self._get_parser('2 * 2 * 2')
        result = parser.parse_term()
        assert result[0].value == 2
        assert result[1].nodes.value == 2
        assert result[2].nodes.value == 2


    def test_complex_expression(self):
        parser = self._get_parser('2 * (3 + 4)')
        result = parser.parse_term()
        pass
        assert result[0].value == 2
        assert result[1].nodes[0].value == 3

    def test_nested_parentheses(self):
        parser = self._get_parser('((3 + 2) * (1 + 1))')
        result = parser.parse_arth_expression()
        assert isinstance(result, Term)
        assert len(result.nodes) == 2
        assert len(result.nodes[0].nodes) == 2
        assert len(result.nodes[1].nodes) == 2
    
    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)

