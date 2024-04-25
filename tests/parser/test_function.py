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

class TestParseParameters:
    ##def test_empty_parameters(self):
    #    parser = self._get_parser('')
    #    results = parser.parse_parameters()
    #    assert len(results) == 0  # Should handle empty parameters correctly

    def test_single_parameter(self):
        parser = self._get_parser('x')
        results = parser.parse_parameters()
        assert len(results) == 1
        assert results['x'].name == 'x'  # Check that the parameter name is parsed correctly

    def test_multiple_parameters(self):
        parser = self._get_parser('x, y, z')
        results = parser.parse_parameters()
        pass
        assert len(results) == 3
        assert (results.get(char).name == char for char in ['x', 'y', 'z'])

    def test_comma_without_parameter(self):
        parser = self._get_parser('x, ')
        with pytest.raises(InvalidParametersDefintion):  # Assuming SyntaxError or a specific custom error is thrown
            parser.parse_parameters()

    def test_duplicate_parameters(self):
        parser = self._get_parser('x, x')
        with pytest.raises(TwoParametersWithTheSameName):  # Assuming SyntaxError or a specific custom error is thrown for duplicates
            parser.parse_parameters()

    #def test_invalid_parameter_name(self):
    #    parser = self._get_parser('(123)')
    #    with pytest.raises(InvalidStatement):  # Assuming invalid parameter names are handled by syntax errors
    #        parser.parse_parameters()

    def test_valid_function_call_with_arguments(self):
        parser = self._get_parser('foo(1, 2, 3)')
        token = parser.try_consume(TokenType.ID)
        result = parser.parse_typical_function_call(token)
        assert result.function_name == 'foo'
        assert len(result.arguments.arguments) == 3

    def test_function_call_without_left_bracket(self):
        parser = self._get_parser('foo 1, 2, 3)')
        token = parser.try_consume(TokenType.ID)
        result = parser.parse_typical_function_call(token)
        assert result is None  # Function call should fail due to missing '('

    def test_function_call_missing_right_bracket(self):
        parser = self._get_parser('foo(1, 2, 3')
        token = parser.try_consume(TokenType.ID)
        with pytest.raises(ExpectedExpressionError):  # Assuming must_be raises this when ')' is missing
            parser.parse_typical_function_call(token)
    
    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)