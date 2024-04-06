from lexer.source.source_position import SourcePosition

class LexerError(Exception):
    def __init__(self, message: str, source_possition: SourcePosition):
        self.message = message
        self.source_possition = source_possition
    
    def __str__(self):
        return f"{self.message}\n"\
        f"in line: {self.source_possition.line}\n"\
        f"column: {self.source_possition.column}"