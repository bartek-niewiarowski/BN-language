import io
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.parser.parser import Parser
from interpreter.parser.syntax_error import *
from interpreter.parser.syntax_tree import *

class TestParseFactor:
    def test_parse_simple_number(self):
        parser = self._get_parser('42')
        result = parser.parse_factor()
        assert hasattr(result, 'value') and result.value == 42

    def test_parse_negated_number(self):
        parser = self._get_parser('-42')
        result = parser.parse_factor()
        assert hasattr(result, 'node') and hasattr(result.node, 'value') and result.node.value == 42

    def test_parse_parentheses_expression(self):
        parser = self._get_parser('(42 + 3)')
        result = parser.parse_factor()
        assert result.left.value == 42
        assert result.right.value == 3

    def test_parse_parentheses_with_negation(self):
        parser = self._get_parser('-(42 + 3)')
        result = parser.parse_factor()
        assert hasattr(result, 'node')
        assert result.node.left.value == 42
        assert result.node.right.value == 3

    def test_parse_incorrect_syntax(self):
        parser = self._get_parser('42 -')
        result = parser.parse_factor()
        assert hasattr(result, 'value')
        with pytest.raises(InvalidFactor):  # Assuming it raises an InvalidStatement error
            parser.parse_factor()

    def test_parse_variable(self):
        parser = self._get_parser('x')
        result = parser.parse_factor()
        assert hasattr(result, 'name')

    def test_no_expression_in_parentheses(self):
        parser = self._get_parser('()')
        assert parser.parse_factor() is None

    def test_empty_input(self):
        parser = self._get_parser('')
        assert parser.parse_factor() is None

    def test_nested_parentheses(self):
        parser = self._get_parser('((42 + 3) * 2)')
        result = parser.parse_factor()
        result.left.left.value == 42
        result.left.right.value == 3
        result.right.value == 2

    def test_function_call(self):
        parser = self._get_parser('myFunction(42)')
        result = parser.parse_factor()
        assert result.function_name == 'myFunction'

    def test_object_expression(self):
        parser = self._get_parser('myObject.property')
        result = parser.parse_factor()
        assert result.parent.name == 'myObject' and result.name == 'property'

    def test_complex_negation(self):
        parser = self._get_parser('-(x + y)')
        result = parser.parse_factor()
        assert result.node.left.name == 'x'
        assert result.node.right.name == 'y'

    def test_invalid_nested_syntax(self):
        parser = self._get_parser('(42 + )')
        with pytest.raises(InvalidArthExpression):
            parser.parse_factor()
    
    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)