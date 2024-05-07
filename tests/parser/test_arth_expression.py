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

class TestParseArthExpression:
    def test_single_term(self):
        parser = self._get_parser('42')
        result = parser.parse_arth_expression()
        pass
        assert isinstance(result, LiteralInt)
        assert result.value == 42

    def test_addition(self):
        parser = self._get_parser('3 + 4')
        result = parser.parse_arth_expression()
        assert isinstance(result[0], LiteralInt)
        assert isinstance(result[1], SumExpression)

    def test_subtraction(self):
        parser = self._get_parser('10 - 2')
        result = parser.parse_arth_expression()
        assert isinstance(result[0], LiteralInt)
        assert isinstance(result[1], SubExpression)
        assert result[1].nodes.value == 2

    def test_combined_addition_subtraction(self):
        parser = self._get_parser('4 + 3 - 2')
        result = parser.parse_arth_expression()
        assert isinstance(result[0], LiteralInt)
        assert isinstance(result[1], SumExpression)
        assert isinstance(result[2], SubExpression)
        assert result[1].nodes.value == 3
        assert result[2].nodes.value == 2

    def test_no_operators(self):
        parser = self._get_parser('x')
        result = parser.parse_arth_expression()
        assert isinstance(result, Identifier)

    def test_invalid_syntax_after_operator(self):
        parser = self._get_parser('x +')
        with pytest.raises(InvalidArthExpression):
            parser.parse_arth_expression()

    def test_complex_expression_with_parentheses(self):
        parser = self._get_parser('2 + (3 * 4)')
        result = parser.parse_arth_expression()
        assert isinstance(result[0], LiteralInt)
        assert len(result[1].nodes) == 2

    def test_unexpected_token(self):
        parser = self._get_parser('2 + x * y')
        result = parser.parse_arth_expression()
        pass
        assert result[0].value == 2
        assert result[1].nodes[0].name == 'x'

    def test_mixed_variable_number_expression(self):
        parser = self._get_parser('x + 5')
        result = parser.parse_arth_expression()
        assert isinstance(result[0], Identifier)
        assert isinstance(result[1], SumExpression)
        assert result[1].nodes.value == 5

    def test_negative_numbers(self):
        parser = self._get_parser('-3 + 5')
        result = parser.parse_arth_expression()
        pass
        assert isinstance(result[0], Negation)
        assert result[0].node.value == 3
        assert result[1].nodes.value == 5

    def test_operator_overloading(self):
        parser = self._get_parser('4 + + 3')
        with pytest.raises(InvalidArthExpression):
            parser.parse_arth_expression()
    
    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)
