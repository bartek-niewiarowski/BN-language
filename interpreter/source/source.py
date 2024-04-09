import io
import typing

from .source_position import SourcePosition

class Source:
    def __init__(self, source:typing.Union[io.TextIOBase, io.StringIO]) -> None:
        self.current_position = SourcePosition(1, 0)
        self.next_position = SourcePosition(1, 1) # usunac to
        self.current_char = 'EOF' # null tutaj lub 'stx'
        self.source = source
        self.next_char()

    def next_char(self):
        # if current_char ==\n to next_line
        # if EOF return
        char = self.source.read(1)

        if char == '\r':
            # Zaglądamy do przodu, aby sprawdzić, czy następnym znakiem jest '\n'.
            currency = self.source.tell()
            next_char = self.source.read(1)
            if next_char == '\n':
                char = '\n'  # Jeśli tak, traktujemy to jako '\n'.
            else:
                # Jeśli nie, cofamy się o jeden znak w źródle, aby nie pominąć znaku.
                self.source.seek(currency) # zapamietac przed reade

        if not char:
            self.current_char = 'EOF'
            self.current_position = SourcePosition(self.next_position.line + 1, 0)
        
        elif char == '\n':
            self.current_char = char
            self.current_position = self.next_position
            self.next_position = self.current_position.next_line()

        else:
            self.current_char = char
            self.current_position = self.next_position
            self.next_position = self.current_position.next_char()

    def get_char(self) -> str:
        return self.current_char

    def get_position(self) -> SourcePosition:
        return self.current_position
