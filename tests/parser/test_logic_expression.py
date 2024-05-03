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

class TestParseLogicExpression:
    def test_single_arithmetic_expression(self):
        parser = self._get_parser('42')
        result = parser.parse_logic_expression()
        assert hasattr(result, 'value') and result.value == 42

    def test_logic_expression_with_equal_operator(self):
        parser = self._get_parser('x == y')
        result = parser.parse_logic_expression()
        pass
        assert hasattr(result, 'left') and hasattr(result.left, 'final_variable')
        assert hasattr(result, 'right') and hasattr(result.right, 'final_variable')

    def test_logic_expression_with_greater_than_operator(self):
        parser = self._get_parser('x > y')
        result = parser.parse_logic_expression()
        assert hasattr(result, 'left') and hasattr(result.left, 'final_variable')
        assert hasattr(result, 'right') and hasattr(result.right, 'final_variable')

    def test_logic_expression_with_multiple_operators(self):
        # Assuming only the first operator is parsed by `parse_logic_expression`
        parser = self._get_parser('x < y == z')
        result = parser.parse_logic_expression()
        assert hasattr(result, 'left') and hasattr(result.left, 'final_variable')
        assert hasattr(result, 'right') and hasattr(result.right, 'final_variable')

    def test_missing_right_expression(self):
        parser = self._get_parser('x <')
        with pytest.raises(InvalidStatement):
            parser.parse_logic_expression()

    def test_invalid_right_expression(self):
        parser = self._get_parser('x < +')
        with pytest.raises(InvalidStatement):
            parser.parse_logic_expression()

    def test_complex_arithmetic_expression(self):
        parser = self._get_parser('3 + 4 > 2')
        result = parser.parse_logic_expression()
        assert hasattr(result, 'left') and hasattr(result.left, 'nodes')
        assert hasattr(result, 'right') and hasattr(result.right, 'value')
    
    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)