import io
import typing

from .source_position import SourcePosition

class Source:
    def __init__(self, source:typing.Union[io.TextIOBase, io.StringIO]) -> None:
        self.current_position = SourcePosition(1, 0)
        # usunieto pole next_position
        self.current_char = 'STX' # null tutaj lub 'stx'
        self.source = source
        self.next_char()

    def next_char(self):
        if self.current_char == '\n':
            self.current_position = self.current_position.next_line()
        char = self.source.read(1)

        if char == '\r':
            currency = self.source.tell()
            next_char = self.source.read(1)
            if next_char == '\n':
                char = '\n'
            else:
                self.source.seek(currency)

        if not char:
            self.current_char = 'EOF'
            self.current_position = self.current_position.next_char()
        
        #elif char == '\n':
        #    self.current_char = char
        #    self.current_position = self.current_position.next_char()
        #    self.current_position.next_line()

        else:
            self.current_char = char
            self.current_position = self.current_position.next_char()

    def get_char(self) -> str:
        return self.current_char

    def get_position(self) -> SourcePosition:
        return self.current_position
