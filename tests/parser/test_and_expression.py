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
        # Check for the correct values of the expressions
        assert all(hasattr(expr, 'position') for expr in result.nodes)

    def test_logic_expression_with_incomplete_and(self):
        parser = self._get_parser('true and')
        with pytest.raises(InvalidStatement):
            parser.parse_and_expression()

    def test_no_initial_expression(self):
        parser = self._get_parser('and true')
        assert parser.parse_and_expression() is None

    def test_and_expression_complex(self):
        parser = self._get_parser('x > 1 and y < 2 and z == 3')
        result = parser.parse_and_expression()
        assert hasattr(result, 'nodes') and len(result.nodes) == 3
        # Assuming that logic expressions check relation and return a structured object

    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)