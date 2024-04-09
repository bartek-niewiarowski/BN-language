from ..source.source import Source
from ..source.source_position import SourcePosition
from ..tokens.token import Token, TokenType
from typing import Optional
from .error import LexerError

## error handler dla Lexera, na niekrytyczne błędy
class Lexer:
    def __init__(self, source:Source, max_string = 1000000, max_int = pow(2,63)-1, max_float=15, max_iden = 40) -> None:
        self._source = source
        self._position = SourcePosition(0, 0)
        self._max_string = max_string
        self._max_int = max_int
        self._max_float = max_float
        self._max_iden = max_iden
        self._current_char = self._source.get_char() # dodano pole przechowujace aktualny znak

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
            ".": TokenType.DOT,
            "$": TokenType.LAMBDA_ID
        }

        self.keywords = {
            "if": TokenType.IF_NAME,
            "else": TokenType.ELSE_NAME,
            "return": TokenType.RETURN_NAME,
            "while": TokenType.WHILE_NAME,
            "break": TokenType.BREAK_NAME,
            "true": TokenType.TRUE_VALUE, #typy tokenow na BOOL_TRUE/BOOL_FALSE
            "false": TokenType.FALSE_VALUE,
            "and": TokenType.AND_OPERATOR,
            "or": TokenType.OR_OPERATOR,
            "def": TokenType.DEF,
            "from": TokenType.FROM_NAME,
            "import": TokenType.IMPORT_NAME
        }

        self.escape_characters = {
            '\\': '\\',
            '"': '"',
            'n': '\n',
            't': '\t',
            'r': '\r',
            'b': '\b',
            'f': '\f',
            'v': '\v',
            'a': '\a',
        }
    
    def _get_char(self) -> str:
        return self._source.get_char()

    def _next_char(self):
        self._position = self._get_position()
        self._source.next_char()
        self._current_char = self._source.get_char()

    def _get_position(self) -> SourcePosition:
        return self._source.get_position()
    
    def _skip_whitespace(self):
        while self._current_char.isspace():
            self._next_char()

    def get_next_token(self) -> Token:
        self._skip_whitespace()

        token = \
            self._build_eof() \
            or self._build_number_value() \
            or self._build_string() \
            or self._build_identifire_or_keyword() \
            or self._build_one_line_operator() \
            or self._build_operators() \
            or self._build_comment()

        if token:
            return token
        raise LexerError("Can't match any token", self._position)
    
    # buduje token komentarza zamiast go pomijac, na tym etapie to parser bedzie odrzucal te tokeny
    def _build_comment(self) -> Optional[Token]:
        if self._current_char != '#':
            return None
        comment_content = []
        while self._current_char != '\n' and self._current_char != 'EOF':
            comment_content.append(self._current_char)
            self._next_char()
        comment = ''.join(comment_content)
        return Token(TokenType.COMMENT, comment, self._position)

    def _build_eof(self) -> Optional[Token]:
        if self._current_char == 'EOF':
            return Token(TokenType.EOF, None, self._get_position()) # none zamiast ''
        return None
    
    def _build_identifire_or_keyword(self) -> Optional[Token]:
        if not self._current_char.isalpha():
            return None
        buffer = []
        while self._current_char is not None and self._current_char not in ['EOF'] and self._current_char.isalpha() or self._current_char.isdecimal():
            if len(buffer) == self._max_iden:
                raise LexerError("Identifier too long", self._get_position())
            buffer.append(self._current_char)
            self._next_char()

        buffer = ''.join(buffer)
        if buffer == '':
            return None
        elif tokenType := self.keywords.get(buffer): # zmiana na tokenType := self.keywords.get(buffer)
            return Token(tokenType, None, self._position)
        else:
            return Token(TokenType.ID, buffer, self._position)
    
    def _build_one_line_operator(self) -> Optional[Token]:
        if tokenType := self.one_line_operators.get(self._current_char): # zmiana na tokenType := self.keywords.get(buffer)
            token = Token(tokenType, None, self._get_position())
            self._next_char()
            return token
        return None
    
    def _build_operators(self) -> Optional[Token]:
        # przekazywanie tylko jednego znaku jako argument
        token = \
            self.build_one_or_two_char_token(
                ("!", TokenType.NEGATION_OPERATOR),
                [("=", TokenType.NOT_EQUAL_OPERATOR)]
            ) or self.build_one_or_two_char_token(
                ("=", TokenType.ASSIGN_OPERATOR),
                [("=", TokenType.EQUAL_OPERATOR),
                (">", TokenType.LAMBDA_OPERATOR)]
            ) or self.build_one_or_two_char_token(
                ("<", TokenType.LESS_THAN_OPERATOR),
                [("=", TokenType.LESS_OR_EQUAL_THAN_OPERATOR)]
            ) or self.build_one_or_two_char_token(
                (">", TokenType.GREATER_THAN_OPERATOR),
                [("=", TokenType.GREATER_OR_EQUAL_THAN_OPERATOR)]
            )
        if token:
            return token
        return None
    
    # dodano escaping, jedak jakie znaki są uzwględnione może się zmienić
    def _build_string(self) -> Optional[Token]:
        if self._current_char != '"':
            return None
        
        escape_counter = 0
        string = []
        self._next_char()
        while self._current_char != '"':
            # wyrzucenie licznika i, sprawdzenie po ilosci elementow w tablicy
            if len(string) == self._max_string:
                raise LexerError("String too long", self._position)
            elif self._current_char == 'EOF' or self._current_char == '\n':
                raise LexerError("Can't match any token, invalid string", self._position)
            elif self._current_char == '\\':
                self._next_char()
                if escape_sequence := self.escape_characters.get(self._current_char):
                    escape_counter += 1
                    string.append(escape_sequence)
                    self._next_char()
                else:
                    string.append('\\')
                    string.append(self._current_char)
            else:
                string.append(self._current_char)
                self._next_char()
        string = ''.join(string)
        self._next_char()
        return(Token(TokenType.STRING_VALUE, string, self._position.get_possition_without_escaping(escape_counter)))
    
    def _build_number_value(self) -> Optional[Token]:
        if not self._get_char().isdecimal():
            return None
        int_part = self.build_int_part()
        if(self._current_char == '.'):
            return self._build_float(int_part)
        return Token(TokenType.INT_VALUE, int_part, self._position)
    
    def _build_float(self, int_part) -> Optional[Token]:
        self._next_char()
        if not self._current_char.isdecimal() and self._current_char != ';':
            raise LexerError("Invalid character in float number, you should use digitals", self._get_position())
        
        fractional_part = 0
        i = 0
        while self._current_char.isdecimal():
            if i == self._max_float:
                raise LexerError("Too many numbers after the decimal point", self._position)
            i+=1
            fractional_part = fractional_part * 10 + int(self._current_char)
            self._next_char()
        total_number = float(int_part) + fractional_part * 10 ** -i
        return(Token(TokenType.FLOAT_VALUE, total_number, self._position))
        
    def build_int_part(self) -> int:
        int_part = 0
        while self._current_char.isdecimal():
            if int_part > (self._max_int - int(self._current_char)) / 10:
                raise LexerError("Integer value too large", self._position)

            int_part = int_part * 10 + int(self._current_char)
            self._next_char()
        return int_part
    
    # lista krotek zamiast 3 tokenow przekazwywanych do funkcji
    def build_one_or_two_char_token(self, one_char_token: tuple[str, TokenType],
                                    two_chars_tokens) -> Optional[Token]:
        one_char_token_value, one_char_token_type = one_char_token
        if self._current_char != one_char_token_value:
            return None

        self._next_char()
        for element in two_chars_tokens:
            if self._current_char == element[0]:
                token = Token(element[1], None, self._source.get_position())
                self._next_char()
                return token  
        return Token(one_char_token_type, None, self._position)

def tokens_generator(lexer: Lexer):
    while (new_token := lexer.get_next_token()).type != TokenType.EOF:
        yield new_token
    yield new_token
