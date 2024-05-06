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

class TestParseProgram:
    def test_multiple_unique_functions(self):
        parser = self._get_parser('def func1() { return (); } def func2() { return (2); }')
        result = parser.parse_program()
        pass
        assert len(result.functions) == 2
        assert 'func1' in result.functions
        assert 'func2' in result.functions

    def test_single_function_definition(self):
        parser = self._get_parser('def singleFunc() { return (42); }')
        result = parser.parse_program()
        assert len(result.functions) == 1
        assert 'singleFunc' in result.functions
        assert isinstance(result.functions['singleFunc'], FunctionDefintion)

    def test_function_redefinition(self):
        parser = self._get_parser('def dupFunc() { return (1); } def dupFunc() { return (2); }')
        with pytest.raises(RedefintionFuntionError):
            parser.parse_program()

    def test_empty_program(self):
        parser = self._get_parser('')
        with pytest.raises(ParsingError):
            parser.parse_program()
    
    def test_function_with_parameters(self):
        parser = self._get_parser('def funcWithParams(x, y) { return (x + y); }')
        result = parser.parse_program()
        assert len(result.functions['funcWithParams'].parameters) == 2
        assert result.functions['funcWithParams'].parameters['x'].name == 'x'
        assert result.functions['funcWithParams'].parameters['y'].name == 'y'
        assert len(result.functions['funcWithParams'].statements) == 1
    
    def test_function_returning_complex_value(self):
        parser = self._get_parser('def complexReturn() { return ([1, 2, 3]); }')
        result = parser.parse_program()
        assert 'complexReturn' in result.functions

    def test_incorrect_function_syntax(self):
        parser = self._get_parser('def wrongFunc(x { return x++; }')
        with pytest.raises(ParsingError):
            parser.parse_program()
    
    def test_function_calling_another(self):
        parser = self._get_parser('def first() { return (1); } def second() { return (first() + 1); }')
        result = parser.parse_program()

    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)