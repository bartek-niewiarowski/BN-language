from dataclasses import dataclass


@dataclass(frozen=True)
class SourcePosition:
    line: int
    column: int
    
    def next_char(self):
        return SourcePosition(self.line, self.column + 1)
    
    def next_line(self):
        return SourcePosition(self.line + 1, 0)
    
    def get_possition_without_escaping(self, n):
        return SourcePosition(self.line, self.column - n)
    
    # dodano equal
    def __eq__(self, other):
        return self.line == other.line and self.column == other.column