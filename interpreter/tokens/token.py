import typing
from .token_type import TokenType

from interpreter.source.source_position import SourcePosition

class Token:
    def __init__(self, type:TokenType, value: typing.Union[str, float, int], position:SourcePosition) -> None:
        self.type = type
        self.value = value
        self.position = position
    
    def __str__(self):
        return f'position: {self.position.line}:{self.position.column},type: {self.type},value: {self.value}'