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

class TestParseOrExpression:
    def test_single_and_expression(self):
        parser = self._get_parser('x > 1')
        result = parser.parse_or_expression()
        assert hasattr(result, 'left') and hasattr(result, 'right')# Depending on the structure of simple expressions

    def test_multiple_and_expressions_with_or(self):
        parser = self._get_parser('x > 1 or y < 2')
        result = parser.parse_or_expression()
        assert hasattr(result, 'nodes') and len(result.nodes) == 2

    def test_or_expression_with_incomplete_and(self):
        parser = self._get_parser('x > 1 or')
        with pytest.raises(InvalidOrExpression):
            parser.parse_or_expression()

    def test_no_initial_expression(self):
        parser = self._get_parser('or y < 2')
        assert parser.parse_or_expression() is None

    def test_or_expression_complex(self):
        parser = self._get_parser('x > 1 or y < 2 or z == 3')
        pass
        result = parser.parse_or_expression()
        assert hasattr(result, 'nodes') and len(result.nodes) == 3

    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)