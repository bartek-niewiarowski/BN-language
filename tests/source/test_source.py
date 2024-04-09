import io
from typing import Tuple, List
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition

class TestSource:
    def test_get_chars_from_string_unix(self):
        string = "ab\nc\nc"
        source = Source(io.StringIO(string))

        char_list, position_list = self.get_chars_and_positions_from_source(source)

        assert char_list == ['a', 'b', '\n', 'c', '\n', 'c', 'EOF']
        assert position_list == [
            SourcePosition(1, 1),
            SourcePosition(1, 2),
            SourcePosition(2, 0),
            SourcePosition(2, 1),
            SourcePosition(3, 0),
            SourcePosition(3, 1),
            SourcePosition(4, 0)
        ]
    
    def test_get_chars_from_string_windows(self):
        string = "a\r\nbc\r\nc"
        source = Source(io.StringIO(string))

        char_list, position_list = self.get_chars_and_positions_from_source(source)
        pass

        assert char_list == ['a', '\n', 'b', 'c', '\n', 'c', 'EOF']
        assert position_list == [
            SourcePosition(1, 1),
            SourcePosition(2, 0),
            SourcePosition(2, 1),
            SourcePosition(2, 2),
            SourcePosition(3, 0),
            SourcePosition(3, 1),
            SourcePosition(4, 0)
        ]

    def test_get_chars_from_file(self):
        with open('tests/data/test_source.bn', 'r') as file:
            source = Source(file)

            char_list, position_list = self.get_chars_and_positions_from_source(source)

            assert char_list == ['a', ',', 'b', '\n', 'a', '\n', 'EOF']
            assert position_list == [
                SourcePosition(1, 1),
                SourcePosition(1, 2),
                SourcePosition(1, 3),
                SourcePosition(2, 0),
                SourcePosition(2, 1),
                SourcePosition(3, 0),
                SourcePosition(4, 0)
            ]

    @staticmethod
    def get_chars_and_positions_from_source(source:Source) -> Tuple[List, List]:
        chars = []
        postions = []

        char = source.get_char()
        chars.append(char)
        postions.append(source.get_position())

        source.next_char()

        while char != 'EOF':
            char = source.get_char()
            postions.append(source.get_position())
            chars.append(char)

            source.next_char()
        
        return chars, postions