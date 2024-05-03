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

class TestParseStatements:
    def test_parse_valid_break_statement(self):
        parser = self._get_parser('break;')
        result = parser.parse_break_statement()
        assert hasattr(result, 'position')

    def test_parse_break_without_semicolon(self):
        parser = self._get_parser('break')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_break_statement()

    def test_parse_without_break_keyword(self):
        parser = self._get_parser('continue;')
        result = parser.parse_break_statement()
        assert result is None
    
    def test_parse_valid_while_statement(self):
        parser = self._get_parser('while (x < 5) { x = x + 1; }')
        result = parser.parse_while_statement()
        assert hasattr(result, 'condition') and hasattr(result, 'statements')
        assert len(result.statements) == 1

    def test_while_without_while_keyword(self):
        parser = self._get_parser('(x < 5) { x = x + 1; }')
        result = parser.parse_while_statement()
        assert result is None

    def test_while_without_left_bracket(self):
        parser = self._get_parser('while x < 5) { x = x + 1; }')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_while_statement()

    def test_while_without_right_bracket(self):
        parser = self._get_parser('while (x < 5 { x = x + 1; }')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_while_statement()

    def test_while_without_condition(self):
        parser = self._get_parser('while () { x = x + 1; }')
        with pytest.raises(InvalidStatement):
            parser.parse_while_statement()

    def test_while_without_statements(self):
        parser = self._get_parser('while (x < 5) {}')
        with pytest.raises(EmptyBlockOfStatements):
            parser.parse_while_statement()
    
    def test_valid_if_statement_without_else(self):
        parser = self._get_parser('if (x > 1) { x = x + 1; }')
        result = parser.parse_if_statement()
        assert hasattr(result, 'condition') and hasattr(result, 'statements')
        assert result.else_statement is None
        assert len(result.statements) == 1

    def test_valid_if_statement_with_else(self):
        parser = self._get_parser('if (x > 1) { x = x + 1; } else { x = x - 1; }')
        result = parser.parse_if_statement()
        assert hasattr(result, 'condition') and hasattr(result, 'statements')
        assert hasattr(result, 'else_statement') and len(result.else_statement) == 1

    def test_if_without_if_keyword(self):
        parser = self._get_parser('(x > 1) { x = x + 1; }')
        result = parser.parse_if_statement()
        assert result is None

    def test_if_without_left_bracket(self):
        parser = self._get_parser('if x > 1) { x = x + 1; }')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_if_statement()

    def test_if_without_right_bracket(self):
        parser = self._get_parser('if (x > 1 { x = x + 1; }')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_if_statement()

    def test_if_without_statements(self):
        parser = self._get_parser('if (x > 1) {}')
        with pytest.raises(EmptyBlockOfStatements):
            parser.parse_if_statement()

    def test_if_with_invalid_condition(self):
        parser = self._get_parser('if () { x = x + 1; }')
        with pytest.raises(EmptyIfCondition):
            parser.parse_if_statement()

    def test_if_else_without_statements(self):
        parser = self._get_parser('if (x > 1) { x = x + 1; } else {}')
        with pytest.raises(EmptyBlockOfStatements):
            parser.parse_if_statement()
    
    def test_valid_return_statement(self):
        parser = self._get_parser('return (x + 1);')
        result = parser.parse_return_statement()
        assert hasattr(result, 'statement')  # Checks if expression is parsed

    def test_return_without_return_keyword(self):
        parser = self._get_parser('(x + 1);')
        result = parser.parse_return_statement()
        assert result is None

    def test_return_missing_left_bracket(self):
        parser = self._get_parser('return x + 1);')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_return_statement()

    def test_return_missing_right_bracket(self):
        parser = self._get_parser('return (x + 1;')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_return_statement()

    def test_return_missing_semicolon(self):
        parser = self._get_parser('return (x + 1)')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_return_statement()
    
    def test_parse_valid_return_statement(self):
        parser = self._get_parser('return (x + 1);')
        assert hasattr(parser.parse_statement(), 'statement')

    def test_parse_valid_if_statement(self):
        parser = self._get_parser('if (x > 1) { x = x + 1; }')
        assert hasattr(parser.parse_statement(), 'condition')

    def test_parse_valid_break_statement_1(self):
        parser = self._get_parser('break;')
        assert hasattr(parser.parse_statement(), 'position')

    def test_parse_valid_while_statement_1(self):
        parser = self._get_parser('while (x < 5) { break; }')
        assert hasattr(parser.parse_statement(), 'condition')

    def test_parse_valid_function_call_or_variable_assignment(self):
        parser = self._get_parser('x = 5;')
        result = parser.parse_statement()
        pass
        assert hasattr(result, 'target')
    
    def test_parse_valid_function_call_or_variable_assignment_1(self):
        parser = self._get_parser('x = sum(a, b);')
        assert hasattr(parser.parse_statement(), 'target')
    
    def test_parse_multiple_statements(self):
        input_code = """
        {
            return (x + 1);
            if (x > 1) { x = x - 1; }
            while (x < 10) { x = x + 1; }
            break;
        }
        """
        parser = self._get_parser(input_code)
        results = parser.parse_statements()
        assert len(results) == 4
        assert hasattr(results[0], 'statement')
        assert hasattr(results[1], 'condition')
        assert hasattr(results[2], 'condition')
        assert hasattr(results[3], 'position')


    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)