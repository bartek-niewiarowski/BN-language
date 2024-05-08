import io
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.tokens.token import Token
from interpreter.tokens.token_type import TokenType
from interpreter.lexer.error import LexerError
from interpreter.source.source_position import SourcePosition

class TestEverySingleToken:
    def test_EOF(self):
        token = self._get_token('')
        assert token.type == TokenType.EOF
    
    def test_comment(self):
        token = self._get_token('#Super jest')
        assert token.type == TokenType.COMMENT
    
    def test_integer(self):
        token = self._get_token('123')
        assert token.type == TokenType.INT_VALUE
        assert token.value == 123
        assert token.position == SourcePosition(1, 1)

    def test_integer_exceeds_limit(self):
        big_int = str(2**64)
        with pytest.raises(LexerError) as exc_info:
            self._get_token(big_int)
    
    def test_float(self):
        token = self._get_token('123.12')
        assert token.type == TokenType.FLOAT_VALUE
        assert token.value == 123.12
        assert token.position == SourcePosition(1, 1)
    
    def test_float_with_semicolon(self):
        token = self._get_token('123.;')
        assert token.type == TokenType.FLOAT_VALUE
        assert token.value == 123.0
        assert token.position == SourcePosition(1, 1)
    
    def test_float_too_many(self):
        with pytest.raises(LexerError) as exc_info:
            self._get_token('123.1234567891234567')
    
    def test_float_no_fraction_part(self):
        with pytest.raises(LexerError) as exc_info:
            self._get_token('4.a')

    def test_string(self):
        token = self._get_token('"Bartek"')
        assert token.type == TokenType.STRING_VALUE
        assert token.value == "Bartek"
        assert token.position == SourcePosition(1, 1)
    
    def test_string_with_wrong_new_line(self):
        with pytest.raises(LexerError) as exc_info:
            self._get_token('"Bartek\n"')
    
    def test_string_with_newline(self):
        token = self._get_token('"Hello\\nWorld"')
        assert token.type == TokenType.STRING_VALUE
        assert token.value == "Hello\nWorld"
        assert token.position == SourcePosition(1, 1)
    
    def test_string_with_many_escape(self):
        token = self._get_token('"\\nHello\\tWorl\\"d"')
        assert token.type == TokenType.STRING_VALUE
        assert token.value == "\nHello\tWorl\"d"
        assert token.position == SourcePosition(1, 1)
    
    def test_true_value(self):
        token = self._get_token('true')
        assert token.type == TokenType.TRUE_VALUE
        assert token.position == SourcePosition(1, 1)
    
    def test_false_value(self):
        token = self._get_token('false')
        assert token.type == TokenType.FALSE_VALUE
        assert token.position == SourcePosition(1, 1)
    
    def test_and_value(self):
        token = self._get_token('and')
        assert token.type == TokenType.AND_OPERATOR
        assert token.position == SourcePosition(1, 1)
    
    def test_or_value(self):
        token = self._get_token('or')
        assert token.type == TokenType.OR_OPERATOR
        assert token.position == SourcePosition(1, 1)
    
    def test_if_keyword(self):
        token = self._get_token('if')
        assert token.type == TokenType.IF_NAME
        assert token.position == SourcePosition(1, 1)

    def test_else_keyword(self):
        token = self._get_token('else')
        assert token.type == TokenType.ELSE_NAME
        assert token.position == SourcePosition(1, 1)

    def test_return_keyword(self):
        token = self._get_token('return')
        assert token.type == TokenType.RETURN_NAME
        assert token.position == SourcePosition(1, 1)

    def test_while_keyword(self):
        token = self._get_token('while')
        assert token.type == TokenType.WHILE_NAME
        assert token.position == SourcePosition(1, 1)

    def test_break_keyword(self):
        token = self._get_token('break')
        assert token.type == TokenType.BREAK_NAME
        assert token.position == SourcePosition(1, 1)

    def test_def_keyword(self):
        token = self._get_token('def')
        assert token.type == TokenType.DEF
        assert token.position == SourcePosition(1, 1)

    def test_from_keyword(self):
        token = self._get_token('from')
        assert token.type == TokenType.FROM_NAME
        assert token.position == SourcePosition(1, 1)

    def test_import_keyword(self):
        token = self._get_token('import')
        assert token.type == TokenType.IMPORT_NAME
        assert token.position == SourcePosition(1, 1)
    
    def test_identifire(self):
        token = self._get_token('x')
        assert token.type == TokenType.ID
        assert token.value == 'x'
        assert token.position == SourcePosition(1, 1)
    
    def test_identifire_longer(self):
        token = self._get_token('BartekNiew')
        assert token.type == TokenType.ID
        assert token.value == 'BartekNiew'
        assert token.position == SourcePosition(1, 1)
    
    def test_identifire_too_long(self):
        with pytest.raises(LexerError) as exc_info:
            self._get_token('BartekNiewBartekNiewBartekNiewBartekNiewaa')
    
    def test_left_bracket(self):
        token = self._get_token('(')
        assert token.type == TokenType.LEFT_BRACKET
        assert token.position == SourcePosition(1, 1)

    def test_right_bracket(self):
        token = self._get_token(')')
        assert token.type == TokenType.RIGHT_BRACKET
        assert token.position == SourcePosition(1, 1)
    
    def test_add_operator(self):
            token = self._get_token('+')
            assert token.type == TokenType.ADD_OPERATOR
            assert token.position == SourcePosition(1, 1)

    def test_sub_operator(self):
        token = self._get_token('-')
        assert token.type == TokenType.SUB_OPERATOR
        assert token.position == SourcePosition(1, 1)

    def test_mul_operator(self):
        token = self._get_token('*')
        assert token.type == TokenType.MUL_OPERATOR
        assert token.position == SourcePosition(1, 1)

    def test_div_operator(self):
        token = self._get_token('/')
        assert token.type == TokenType.DIV_OPERATOR
        assert token.position == SourcePosition(1, 1)

    def test_left_curly_bracket(self):
        token = self._get_token('{')
        assert token.type == TokenType.LEFT_CURLY_BRACKET
        assert token.position == SourcePosition(1, 1)

    def test_right_curly_bracket(self):
        token = self._get_token('}')
        assert token.type == TokenType.RIGHT_CURLY_BRACKET
        assert token.position == SourcePosition(1, 1)

    def test_left_square_bracket(self):
        token = self._get_token('[')
        assert token.type == TokenType.LEFT_QUADRATIC_BRACKET
        assert token.position == SourcePosition(1, 1)

    def test_right_square_bracket(self):
        token = self._get_token(']')
        assert token.type == TokenType.RIGHT_QUADRATIC_BRACKET
        assert token.position == SourcePosition(1, 1)

    def test_semicolon(self):
        token = self._get_token(';')
        assert token.type == TokenType.SEMICOLON
        assert token.position == SourcePosition(1, 1)

    def test_comma(self):
        token = self._get_token(',')
        assert token.type == TokenType.COMMA
        assert token.position == SourcePosition(1, 1)

    def test_dot(self):
        token = self._get_token('.')
        assert token.type == TokenType.DOT
        assert token.position == SourcePosition(1, 1)
    
    def test_lambda_id(self):
        token = self._get_token('$')
        assert token.type == TokenType.LAMBDA_ID
        assert token.position == SourcePosition(1, 1)

    def test_less_or_equal(self):
        token = self._get_token('<=')
        assert token.type == TokenType.LESS_OR_EQUAL_THAN_OPERATOR
        assert token.position == SourcePosition(1, 2)
    
    def test_less(self):
        token = self._get_token('<')
        assert token.type == TokenType.LESS_THAN_OPERATOR
        assert token.position == SourcePosition(1, 1)
    
    def test_greater_or_equal(self):
        token = self._get_token('>=')
        assert token.type == TokenType.GREATER_OR_EQUAL_THAN_OPERATOR
        assert token.position == SourcePosition(1, 2)
    
    def test_greater(self):
        token = self._get_token('>')
        assert token.type == TokenType.GREATER_THAN_OPERATOR
        assert token.position == SourcePosition(1, 1)
    
    def test_equal(self):
        token = self._get_token('==')
        assert token.type == TokenType.EQUAL_OPERATOR
        assert token.position == SourcePosition(1, 2)
    
    def test_lambda_operator(self):
        token = self._get_token('=>')
        assert token.type == TokenType.LAMBDA_OPERATOR
        assert token.position == SourcePosition(1, 2)
    
    def test_not_equal(self):
        token = self._get_token('!=')
        assert token.type == TokenType.NOT_EQUAL_OPERATOR
        assert token.position == SourcePosition(1, 2)
    
    def test_assign(self):
        token = self._get_token('=')
        assert token.type == TokenType.ASSIGN_OPERATOR
        assert token.position == SourcePosition(1, 1)

    def test_negation(self):
        token = self._get_token('!')
        assert token.type == TokenType.NEGATION_OPERATOR
        assert token.position == SourcePosition(1, 1)
    
    def test_no_match_token(self):
        with pytest.raises(LexerError) as exc_info:
            self._get_token('_')

    @staticmethod
    def _get_token(string: str) -> Token:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return lexer.get_next_token()
