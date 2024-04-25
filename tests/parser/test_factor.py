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

class TestParseFactor:
    def test_parse_simple_number(self):
        parser = self._get_parser('42')
        result = parser.parse_factor()
        assert isinstance(result, LiteralInt)
        assert result.value == 42

    def test_parse_negated_number(self):
        parser = self._get_parser('-42')
        result = parser.parse_factor()
        assert isinstance(result, Negation)
        assert isinstance(result.node, LiteralInt)
        assert result.node.value == 42

    def test_multiple_negations(self):
        parser = self._get_parser('---42')
        result = parser.parse_factor()
        assert isinstance(result, Negation)
        assert isinstance(result.node, Negation)
        assert isinstance(result.node.node, Negation)
        assert result.node.node.node.value == 42

    def test_parse_parentheses_expression(self):
        parser = self._get_parser('(42 + 3)')
        result = parser.parse_factor()
        assert isinstance(result, ArthExpression)  # Assuming ArthExpression handles inside of parentheses

    def test_parse_parentheses_with_negation(self):
        parser = self._get_parser('-(42 + 3)')
        result = parser.parse_factor()
        assert isinstance(result, Negation)
        assert isinstance(result.node, ArthExpression)

    def test_parse_incorrect_syntax(self):
        parser = self._get_parser('42 -')
        result = parser.parse_factor()
        assert result.value == 42
        with pytest.raises(InvalidStatement):
            parser.parse_factor()

    def test_parse_variable(self):
        parser = self._get_parser('x')
        result = parser.parse_factor()
        pass
        assert isinstance(result, Identifier)
        assert result.name == 'x'

    def test_no_expression_in_parentheses(self):
        parser = self._get_parser('()')
        with pytest.raises(InvalidStatement):
            parser.parse_factor()

    def test_empty_input(self):
        parser = self._get_parser('')
        with pytest.raises(InvalidStatement):
            parser.parse_factor()
    
    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)