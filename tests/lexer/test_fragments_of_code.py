import io
import pytest
from typing import List

from interpreter.lexer.lexer import Lexer, tokens_generator
from interpreter.source.source import Source
from interpreter.tokens.token import Token, TokenType
from interpreter.lexer.error import LexerError
from interpreter.source.source_position import SourcePosition

class TestFragmentsOfCode:
    def test_variable(self):
            tokens = self._get_tokens_from_string('x = 10;\nx=5;')
            pass
            #assert [token.type for token in tokens] == [TokenType.ID, TokenType.ASSIGN_OPERATOR, TokenType.INT_VALUE,
            #                   TokenType.SEMICOLON, TokenType.EOF]

            assert tokens == [
                Token(TokenType.ID, 'x', SourcePosition(1, 1)),
                Token(TokenType.ASSIGN_OPERATOR, None,SourcePosition(1, 3)),
                Token(TokenType.INT_VALUE, 10, SourcePosition(1, 6)),
                Token(TokenType.SEMICOLON, None,SourcePosition(1, 7)),
                Token(TokenType.ID, 'x', SourcePosition(2, 1)),
                Token(TokenType.ASSIGN_OPERATOR, None,SourcePosition(2, 2)),
                Token(TokenType.INT_VALUE, 5, SourcePosition(2, 3)),
                Token(TokenType.SEMICOLON, None,SourcePosition(2, 4)),
                Token(TokenType.EOF, None, SourcePosition(3, 0))
            ]
    
    def test_array_with_different_types(self):
        tokens = self._get_tokens_from_string('list = [10, 22.22, 12, "Bartek", [1, 2, 3]];')
        assert [token.type for token in tokens] == [
            TokenType.ID, TokenType.ASSIGN_OPERATOR, TokenType.LEFT_QUADRATIC_BRACKET, 
            TokenType.INT_VALUE, TokenType.COMMA,
            TokenType.FLOAT_VALUE, TokenType.COMMA,
            TokenType.INT_VALUE, TokenType.COMMA,
            TokenType.STRING_VALUE, TokenType.COMMA,
            TokenType.LEFT_QUADRATIC_BRACKET,
            TokenType.INT_VALUE, TokenType.COMMA,
            TokenType.INT_VALUE, TokenType.COMMA,
            TokenType.INT_VALUE,
            TokenType.RIGHT_QUADRATIC_BRACKET, TokenType.RIGHT_QUADRATIC_BRACKET,
            TokenType.SEMICOLON, TokenType.EOF
        ]
    
    def test_assignment_with_different_data_types(self):
        tokens = self._get_tokens_from_string('x = 10; y = "text"; z = true;')
        assert [token.type for token in tokens] == [
            TokenType.ID, TokenType.ASSIGN_OPERATOR, TokenType.INT_VALUE,
            TokenType.SEMICOLON, TokenType.ID, TokenType.ASSIGN_OPERATOR, TokenType.STRING_VALUE,
            TokenType.SEMICOLON, TokenType.ID, TokenType.ASSIGN_OPERATOR, TokenType.TRUE_VALUE,
            TokenType.SEMICOLON, TokenType.EOF
        ]
    
    def test_while_loop_with_break(self):
        tokens = self._get_tokens_from_string('while (x < 5) { x = x + 1; if (x == 3) break; }')
        pass
        assert [token.type for token in tokens] == [
            TokenType.WHILE_NAME, TokenType.LEFT_BRACKET, TokenType.ID, TokenType.LESS_THAN_OPERATOR, 
            TokenType.INT_VALUE, TokenType.RIGHT_BRACKET, TokenType.LEFT_CURLY_BRACKET, 
            TokenType.ID, TokenType.ASSIGN_OPERATOR, TokenType.ID, TokenType.ADD_OPERATOR, 
            TokenType.INT_VALUE, TokenType.SEMICOLON, TokenType.IF_NAME, TokenType.LEFT_BRACKET, 
            TokenType.ID, TokenType.EQUAL_OPERATOR, TokenType.INT_VALUE, TokenType.RIGHT_BRACKET, 
            TokenType.BREAK_NAME, TokenType.SEMICOLON, TokenType.RIGHT_CURLY_BRACKET, TokenType.EOF
        ]
    
    def test_function_definition_with_return(self):
        tokens = self._get_tokens_from_string('def myFunc() { return x; }')
        assert [token.type for token in tokens] == [
            TokenType.DEF, TokenType.ID, TokenType.LEFT_BRACKET, TokenType.RIGHT_BRACKET, 
            TokenType.LEFT_CURLY_BRACKET, TokenType.RETURN_NAME, TokenType.ID, 
            TokenType.SEMICOLON, TokenType.RIGHT_CURLY_BRACKET, TokenType.EOF
        ]
    
    def test_function_with_multiple_statements_including_conditional_and_loop(self):
        tokens = self._get_tokens_from_string('''
        def myFunc(x) {
            if (x > 0) {
                while (x < 10) {
                    x = x + 1;
                }
            }
            return x;
        }''')
        assert [token.type for token in tokens] == [
            TokenType.DEF, TokenType.ID, TokenType.LEFT_BRACKET, TokenType.ID, 
            TokenType.RIGHT_BRACKET, TokenType.LEFT_CURLY_BRACKET, TokenType.IF_NAME, 
            TokenType.LEFT_BRACKET, TokenType.ID, TokenType.GREATER_THAN_OPERATOR, 
            TokenType.INT_VALUE, TokenType.RIGHT_BRACKET, TokenType.LEFT_CURLY_BRACKET, 
            TokenType.WHILE_NAME, TokenType.LEFT_BRACKET, TokenType.ID, 
            TokenType.LESS_THAN_OPERATOR, TokenType.INT_VALUE, TokenType.RIGHT_BRACKET, 
            TokenType.LEFT_CURLY_BRACKET, TokenType.ID, TokenType.ASSIGN_OPERATOR, 
            TokenType.ID, TokenType.ADD_OPERATOR, TokenType.INT_VALUE, 
            TokenType.SEMICOLON, TokenType.RIGHT_CURLY_BRACKET, TokenType.RIGHT_CURLY_BRACKET, 
            TokenType.RETURN_NAME, TokenType.ID, TokenType.SEMICOLON, 
            TokenType.RIGHT_CURLY_BRACKET, TokenType.EOF
        ]

    def test_import_statement(self):
        tokens = self._get_tokens_from_string('from MyModule import Student;')
        assert [token.type for token in tokens] == [
            TokenType.FROM_NAME, TokenType.ID,
            TokenType.IMPORT_NAME, TokenType.ID, 
            TokenType.SEMICOLON, TokenType.EOF
        ]
    
    @staticmethod
    def _get_tokens_from_string(string: str) -> List[Token]:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)

        return list(tokens_generator(lexer))
