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

class TestParseandExpression:
    def test_single_logic_expression(self):
        parser = self._get_parser('true')
        result = parser.parse_and_expression()
        assert hasattr(result, 'position')

    def test_multiple_logic_expressions_with_and(self):
        parser = self._get_parser('true and false')
        result = parser.parse_and_expression()
        pass
        assert hasattr(result, 'nodes') and len(result.nodes) == 2
        assert all(hasattr(expr, 'position') for expr in result.nodes)

    def test_logic_expression_with_incomplete_and(self):
        parser = self._get_parser('true and')
        with pytest.raises(InvalidAndExpression):
            parser.parse_and_expression()

    def test_no_initial_expression(self):
        parser = self._get_parser('and true')
        assert parser.parse_and_expression() is None

    def test_and_expression_complex(self):
        parser = self._get_parser('x > 1 and y < 2 and z == 3')
        result = parser.parse_and_expression()
        assert hasattr(result, 'nodes') and len(result.nodes) == 3

    def test_nested_logic_expressions(self):
        parser = self._get_parser('true and false and true')
        result = parser.parse_and_expression()
        assert hasattr(result, 'nodes') and len(result.nodes) == 3

    def test_extra_spaces_and_unusual_whitespace(self):
        parser = self._get_parser('true     and      false')
        result = parser.parse_and_expression()
        assert len(result.nodes) == 2

    def test_syntax_errors_in_expressions(self):
        parser = self._get_parser('true and (false')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_and_expression()

    def test_combination_of_logical_and_relational(self):
        parser = self._get_parser('true and x > 5')
        result = parser.parse_and_expression()
        assert len(result.nodes) == 2 and isinstance(result.nodes[1], GreaterOperation)

    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)