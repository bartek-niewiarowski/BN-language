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
        assert isinstance(result, Term)
        assert len(result.nodes) == 2
        assert all(isinstance(expr, LiteralInt) for expr in result.nodes)

    def test_division(self):
        parser = self._get_parser('10 / 2')
        result = parser.parse_term()
        assert isinstance(result, Term)
        assert len(result.nodes) == 2
        assert isinstance(result.nodes[1], Reciprocal)
        assert result.nodes[1].node.value == 2

    def test_combined_multiplication_division(self):
        parser = self._get_parser('4 * 3 / 2')
        result = parser.parse_term()
        assert isinstance(result, Term)
        assert len(result.nodes) == 3
        assert isinstance(result.nodes[2], Reciprocal)
        assert result.nodes[2].node.value == 2

    def test_no_operators(self):
        parser = self._get_parser('x')
        result = parser.parse_term()
        assert isinstance(result, ObjectExpression)
        assert result.final_variable.name == 'x'

    def test_invalid_syntax_after_operator(self):
        parser = self._get_parser('x *')
        with pytest.raises(InvalidTerm):
            parser.parse_term()

    def test_division_by_zero_static(self):
        parser = self._get_parser('x / 0')
        result = parser.parse_term()
        assert isinstance(result, Term)
        assert isinstance(result.nodes[1], Reciprocal)
        assert result.nodes[1].node.value == 0

    def test_chained_multiplications(self):
        parser = self._get_parser('2 * 2 * 2')
        result = parser.parse_term()
        assert isinstance(result, Term)
        assert len(result.nodes) == 3
        assert all(isinstance(expr, LiteralInt) and expr.value == 2 for expr in result.nodes)

    def test_complex_expression(self):
        parser = self._get_parser('2 * (3 + 4)')
        result = parser.parse_term()
        assert isinstance(result, Term)
        assert len(result.nodes) == 2
        assert isinstance(result.nodes[1], ArthExpression)  # Assuming this parses as an arithmetic expression

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

