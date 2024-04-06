import io

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.tokens.token import Token, TokenType

class TestEverySingleToken:
    def test_EOF(self):
        token = self._get_token('')
        assert token.type == TokenType.EOF

    @staticmethod
    def _get_token(string: str) -> Token:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return lexer.get_next_token()