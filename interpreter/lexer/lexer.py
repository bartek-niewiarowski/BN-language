from source.source import Source
from source.source_position import SourcePosition
from tokens.token import Token, TokenType
from typing import Optional
from .lexer.error import LexerError
import io

class Lexer:
    def __init__(self, source:Source, max_string = 1e9, max_int = pow(2,63)-1, max_float=15, max_iden = 40) -> None:
        self._source = source
        self._position = SourcePosition(0, 0)
        self._max_string = max_string
        self._max_int = max_int
        self._max_float = max_float
        self._max_iden = max_iden

        self.one_line_operators = {
            "+": TokenType.ADD_OPERATOR,
            "-": TokenType.SUB_OPERATOR,
            "*": TokenType.MUL_OPERATOR,
            "/": TokenType.DIV_OPERATOR,
            "(": TokenType.LEFT_BRACKET,
            ")": TokenType.RIGHT_BRACKET,
            "{": TokenType.LEFT_CURLY_BRACKET,
            "}": TokenType.RIGHT_CURLY_BRACKET,
            "[": TokenType.LEFT_QUADRATIC_BRACKET,
            "]": TokenType.RIGHT_QUADRATIC_BRACKET,
            ";": TokenType.SEMICOLON,
            ",": TokenType.COMMA,
            ".": TokenType.DOT
        }

        self.keywords = {
            "if": TokenType.IF_NAME,
            "else": TokenType.ELSE_NAME,
            "return": TokenType.RETURN_NAME,
            "while": TokenType.WHILE_NAME,
            "break": TokenType.BREAK_NAME,
            "true": TokenType.BOOL_VALUE,
            "false": TokenType.BOOL_VALUE,
            "and": TokenType.AND_OPERATOR,
            "or": TokenType.OR_OPERATOR,
            "def": TokenType.DEF,
            "from": TokenType.FROM_NAME,
            "import": TokenType.IMPORT_NAME
        }
    
    def _get_char(self) -> str:
        return self._source.get_char()

    def _next_char(self):
        self._position = self._get_position
        return self._get_char()

    def _get_position(self) -> SourcePosition:
        return self._source.get_position()
    
    def _skip_whitespace(self):
        char = self._get_char()
        while char.isspace():
            self._next_char()
            char = self._get_char()
    
    def _skip_comment(self):
        char = self._get_char()
        if char != '#':
            return
        while char != '\n':
            self._next_char()
            char = self._get_char()
        self._next_char

    def get_next_token(self) -> Token:
        self._skip_whitespace()
        self._skip_comment()

        token = \
            self._build_eof() \
            or self._build_number_value() \
            or self._build_string() \
            or self._build_operators() \
            or self._build_one_line_operator \
            or self._build_identifire_or_keyword() \

        if token:
            return token

        raise LexerError("Can't match any token", self._previous_position)

    def _build_eof(self) -> Optional[Token]:
        if self._get_char() == 'EOF':
            return Token(TokenType.EOF, '', self._get_position())
        return None
    
    def _build_identifire_or_keyword(self) -> Optional[Token]:
        buffer = []
        char = self._get_char()

        if not char.isalpha():
            return None

        i = 0
        while char.isalpha() or char.isdigit():
            if i == self._max_iden:
                raise LexerError("Identifier too long", self._get_position())
            i+=1
            buffer.append(char)
            self._next_char()
            char = self._get_char()

        buffer = ''.join(buffer)
        if buffer == '':
            return None
        elif buffer in self.keywords:
            if(buffer in ['true', 'false']):
                return Token(TokenType.BOOL_VALUE, buffer, self._position)
            if(buffer == 'and'):
                return Token(TokenType.AND_OPERATOR, buffer, self._position)
            if(buffer == 'or'):
                return Token(TokenType.OR_OPERATOR, buffer, self._position)
            return Token(self.keywords[buffer], '', self._position)
        else:
            return Token(TokenType.ID, buffer, self._position)
    
    def _build_one_line_operator(self) -> Optional[Token]:
        char = self._get_char()

        if char in self.one_line_operators:
            self._next_char()
            return Token(self.one_line_operators[char], '', self._position)
        return None
    
    def _build_operators(self) -> Optional[Token]:
        token = \
            self.build_one_or_two_char_token(
                ("!", TokenType.NEGATION_OPERATOR),
                ("!=", TokenType.NOT_EQUAL_OPERATOR)
            ) or self.build_one_or_two_char_token(
                ("=", TokenType.ASSIGN_OPERATOR),
                ("==", TokenType.EQUAL_OPERATOR)
            ) or self.build_one_or_two_char_token(
                ("<", TokenType.LESS_THAN_OPERATOR),
                ("<=", TokenType.LESS_THAN_OR_EQUAL_OPERATOR)
            ) or self.build_one_or_two_char_token(
                (">", TokenType.GREATER_THAN_OPERATOR),
                (">=", TokenType.GREATER_THAN_OPERATOR_OR_EQUAL)
            )
        if token:
            return token
        return None
    
    def _build_string(self) -> Optional[Token]:
        string = []

        char = self._get_char()
        if char != '"':
            return None
        
        i = 0
        self._next_char()
        char = self._get_char()

        while char != '"':
            if i == self._max_string:
                raise LexerError("String too long", self._position)
            if char == 'EOF':
                raise LexerError("Can't match any token, invalid string", self._position)
            i+=1
            string.append(char)
            self._next_char()
            char = self._get_char()
        string = ''.join(string)
        self._next_char()
        return(Token(TokenType.STRING_VALUE, string, self._position))
    
    def _build_number_value(self) -> Optional[Token]:
        if not self._get_char().isdigit():
            return None
        
        int_part = self.build_int_part()

        if(self._get_char() == '.'):
            return self._build_float(int_part)
        return Token(TokenType.INT_VALUE, int_part, self._position)
    
    def _build_float(self, int_part) -> Optional[Token]:
        self._next_char()
        char = self._get_char()
        if not char.isdigit():
            raise LexerError("Invalid character in float number, you should use digitals", self._get_position())
    
        fractional_part = 0
        i = 0
        while char.isdigit():
            if i == self._max_float:
                raise LexerError("Too many numbers after the decimal point", self._position)
            i+=1

            fractional_part = fractional_part * 10 + int(char)
            self._next_char()
            char = self._get_char()
        total_number = float(int_part) + fractional_part * 10 ** -i
        return(Token(TokenType.FLOAT_VALUE, total_number, self._position))
        
    def build_int_part(self) -> int:
        char = self._get_char()
        int_part = 0
        while char.isdigit():
            if int_part > self._max_int:
                raise LexerError("Integer value too large", self._position)

            int_part = int_part * 10 + int(char)
            self._next_char()
            char = self._get_char()
        return int_part
    
    def build_one_or_two_char_token(self, one_char_token: tuple[str, TokenType],
                                    two_chars_token: tuple[str, TokenType]) -> Optional[Token]:
        one_char_token_value, one_char_token_type = one_char_token
        two_chars_token_value, two_chars_token_type = two_chars_token

        if self._get_char() != one_char_token_value:
            return None

        self._next_char()
        if self._get_char() == two_chars_token_value[1]:
            self._next_char()
            return Token(two_chars_token_type, '', self._position())
        else:
            return Token(one_char_token_type, '', self._position)
