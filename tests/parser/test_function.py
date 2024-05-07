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
    def test_empty_parameters(self):
        parser = self._get_parser('')
        results = parser.parse_parameters()
        assert len(results) == 0  # Should handle empty parameters correctly

    def test_single_parameter(self):
        parser = self._get_parser('x')
        results = parser.parse_parameters()
        assert len(results) == 1
        assert results[0] == 'x'  # Check that the parameter name is parsed correctly

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

    def test_valid_function_call_with_arguments(self):
        parser = self._get_parser('foo(1, 2, 3)')
        token = parser.try_consume(TokenType.ID)
        result = parser.parse_typical_function_call(token, None)
        assert result.function_name == 'foo'
        assert len(result.arguments.arguments) == 3

    def test_function_call_without_left_bracket(self):
        parser = self._get_parser('foo 1, 2, 3)')
        token = parser.try_consume(TokenType.ID)
        result = parser.parse_typical_function_call(token, None)
        assert result is None  # Function call should fail due to missing '('

    def test_function_call_missing_right_bracket(self):
        parser = self._get_parser('foo(1, 2, 3')
        token = parser.try_consume(TokenType.ID)
        with pytest.raises(ExpectedExpressionError):  # Assuming must_be raises this when ')' is missing
            parser.parse_typical_function_call(token, None)
    
    def test_single_variable(self):
        parser = self._get_parser('x')
        result = parser.parse_chained_expression()
        assert result.name == 'x'  # Assuming the parse_id function returns an object with a name attribute for identifiers

    def test_multiple_variables_chained(self):
        parser = self._get_parser('x.y.z')
        result = parser.parse_chained_expression()
        assert isinstance(result, Identifier)
        assert isinstance(result.parent, Identifier)
        assert isinstance(result.parent.parent, Identifier)
        assert result.parent.parent.parent is None

    def test_variable_and_function_call_chained(self):
        parser = self._get_parser('x.y().z()')
        result = parser.parse_chained_expression()
        assert isinstance(result, FunctionCall)  # Assuming TypicalFunctionCall for function calls

    def test_no_initial_identifier(self):
        parser = self._get_parser('')
        result = parser.parse_chained_expression()
        assert result is None

    def test_dot_without_following_identifier(self):
        parser = self._get_parser('x.')
        with pytest.raises(ParsingError):
            parser.parse_chained_expression()

    def test_complex_chained_expression(self):
        parser = self._get_parser('obj.method().nextMethod().field')
        result = parser.parse_chained_expression()
        assert isinstance(result, Identifier)
        
    
    def test_function_call(self):
        parser = self._get_parser('obj.method().nextMethod();')
        result = parser.parse_function_call_or_assignment()
        assert isinstance(result, FunctionCall)
    
    def test_function_call_with_args(self):
        parser = self._get_parser('obj.sum(a+b);')
        result = parser.parse_function_call_or_assignment()
        pass
        assert isinstance(result, FunctionCall)
        assert len(result.arguments.arguments) == 1
     
    def test_function_call_with_no_chaining(self):
        parser = self._get_parser('doSomething();')
        result = parser.parse_function_call_or_assignment()
        assert isinstance(result, FunctionCall)  # Assume FunctionCall is the expected type for simple calls

    def test_chained_function_call(self):
        parser = self._get_parser('object.doSomething();')
        result = parser.parse_function_call_or_assignment()
        assert isinstance(result, FunctionCall)
        assert result.parent.name == 'object'

    def test_variable_assignment_simple(self):
        parser = self._get_parser('x = 42;')
        result = parser.parse_function_call_or_assignment()
        assert isinstance(result, Assignment)
        assert result.target.name == 'x'
        assert isinstance(result.value, LiteralInt)

    def test_missing_semicolon_in_function_call(self):
        parser = self._get_parser('doSomething()')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_function_call_or_assignment()

    def test_chained_assignment(self):
        parser = self._get_parser('obj.attr = "value";')
        result = parser.parse_function_call_or_assignment()
        assert isinstance(result, Assignment)
        assert isinstance(result.value, LiteralString)
        assert result.target.name == 'attr'
        assert result.value.value == "value"

    def test_valid_lambda_expression(self):
        parser = self._get_parser('$x => { x = x + 1; }')
        result = parser.parse_lambda_expression()
        assert isinstance(result, LambdaExpression)
        assert result.variable_name == 'x'
        assert len(result.statements.statements) == 1

    def test_lambda_without_lambda_id(self):
        parser = self._get_parser('x => { x = x + 1; }')
        result = parser.parse_lambda_expression()
        assert result is None

    def test_lambda_missing_variable_name(self):
        parser = self._get_parser('$ => { x = x + 1; }')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_lambda_expression()

    def test_lambda_missing_lambda_operator(self):
        parser = self._get_parser('$x { x = x + 1; }')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_lambda_expression()

    def test_lambda_missing_statements(self):
        parser = self._get_parser('$x => {}')
        with pytest.raises(EmptyBlockOfStatements):
            parser.parse_lambda_expression()

    def test_lambda_incorrect_statements(self):
        parser = self._get_parser('$x => { y = }')
        with pytest.raises(InvalidVariableAssignment):
            parser.parse_lambda_expression()
    
    def test_valid_function_definition(self):
        parser = self._get_parser('def myFunction(x, y) { return x + y; };')
        result = parser.parse_function_definition()
        assert isinstance(result, FunctionDefintion)
        assert result.name == 'myFunction'
        assert len(result.parameters) == 2
        assert len(result.statements.statements) == 1

    def test_function_definition_without_def(self):
        parser = self._get_parser('myFunction(x, y) { return (x + y); }')
        result = parser.parse_function_definition()
        assert result is None

    def test_missing_parentheses_around_parameters(self):
        parser = self._get_parser('def myFunction x, y { return (x + y); }')
        with pytest.raises(ExpectedExpressionError):
            parser.parse_function_definition()

    def test_empty_statement_block(self):
        parser = self._get_parser('def myFunction(x, y) {};')
        with pytest.raises(EmptyBlockOfStatements):
            parser.parse_function_definition()

    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)