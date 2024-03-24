from lexer.source.source import Source
from lexer.source.source_position import SourcePosition

class Lexer:
    def __init__(self, source:Source, max_string = 1e9, max_int = pow(2, 63)-1, max_float=15) -> None:
        self._source = source
        self._position = SourcePosition(0, 0)
        self._max_string = max_string
        self._max_int = max_int
        self._max_float = max_float