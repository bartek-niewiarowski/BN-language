import io
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.tokens.token_type import TokenType
from interpreter.source.source_position import SourcePosition
from interpreter.parser.parser import Parser
from interpreter.parser.syntax_error import *
from interpreter.parser.syntax_tree import *

class TestParser:
    def test_init_parser(self):
        parser = self._get_parser('x')
        assert parser.current_token.type == TokenType.ID

    def test_consume_token(self):
        parser = self._get_parser('x = 10;')
        types = [TokenType.ID, TokenType.ASSIGN_OPERATOR, TokenType.INT_VALUE, TokenType.SEMICOLON]
        for type in types:
            assert parser.current_token.type == type
            parser.consume_token()
    
    def test_consume_token_with_comment(self):
        parser = self._get_parser('#abc#xda\nx = 10;')
        types = [TokenType.ID, TokenType.ASSIGN_OPERATOR, TokenType.INT_VALUE, TokenType.SEMICOLON]
        for type in types:
            assert parser.current_token.type == type
            parser.consume_token()
    
    def test_try_consume(self):
        parser = self._get_parser('x = 10;')
        token = parser.try_consume(TokenType.ID)
        assert token.type == TokenType.ID
        assert token.value == 'x'
        assert token.position == SourcePosition(1, 1)
    
    def test_try_consume_invalid_type(self):
        parser = self._get_parser('x = 10;')
        token = parser.try_consume(TokenType.LEFT_BRACKET)
        assert token is None
    
    def test_try_consume_with_list(self):
        parser = self._get_parser('-')
        token = parser.try_consume([TokenType.ADD_OPERATOR, TokenType.SUB_OPERATOR])
        assert token.type == TokenType.SUB_OPERATOR
        assert token.position == SourcePosition(1,1)
    
    def test_must_be(self):
        parser = self._get_parser('x = 10;')
        token = parser.must_be(TokenType.ID)
        assert token.type == TokenType.ID
        assert token.value == 'x'
        assert token.position == SourcePosition(1, 1)
    
    def test_must_be_invalid_type(self):
        parser = self._get_parser('x = 10;')
        with pytest.raises(ExpectedExpressionError):
            parser.must_be(TokenType.ADD_OPERATOR)
    
    def test_parse_boolean_true(self):
        parser = self._get_parser('true')
        result = parser.parse_boolean()
        assert result and result.position == SourcePosition(1, 1)

    def test_parse_boolean_false(self):
        parser = self._get_parser('false')
        result = parser.parse_boolean()
        assert result and result.position == SourcePosition(1, 1)

    def test_parse_boolean_none(self):
        parser = self._get_parser('10')
        result = parser.parse_boolean()
        assert result is None

    def test_parse_number(self):
        parser = self._get_parser('123')
        result = parser.parse_number()
        assert result and result.position == SourcePosition(1, 1) and result.value == 123

    def test_parse_number_none(self):
        parser = self._get_parser('abc')
        result = parser.parse_number()
        assert result is None

    def test_parse_float(self):
        parser = self._get_parser('123.45')
        result = parser.parse_float()
        assert result and result.position == SourcePosition(1, 1) and result.value == 123.45

    def test_parse_float_none(self):
        parser = self._get_parser('abc')
        result = parser.parse_float()
        assert result is None

    def test_parse_string(self):
        parser = self._get_parser('"hello"')
        result = parser.parse_string()
        assert result and result.position == SourcePosition(1, 1) and result.value == 'hello'

    def test_parse_string_none(self):
        parser = self._get_parser('123')
        result = parser.parse_string()
        assert result is None
    
    def test_parse_array(self):
        parser = self._get_parser("[1, 2, 3]")
        result = parser.parse_array()
        assert len(result.items) == 3

    def test_valid_function_definition(self):
        parser = TestParser._get_parser('def myFunction(x, y) { return x; }')
        result = parser.parse_function_definition({})
        assert result.name == "myFunction"
        assert len(result.parameters) == 2
        assert isinstance(result.statements.statements[0], ReturnStatement)
    
    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)
