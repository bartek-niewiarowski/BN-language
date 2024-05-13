import io
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.parser.parser import Parser
from interpreter.parser.syntax_error import *
from interpreter.parser.syntax_tree import *
from interpreter.interpreter.executeVisitor import ExecuteVisitor
from interpreter.interpreter.interpreter import Context

class TestInterpreter:
    def test_false_expression(self):
        parser = self._get_parser('true and false')
        result = parser.parse_and_expression()
        context = Context()
        visitor = ExecuteVisitor()
        a = visitor.visit_and_expression(result, context)
        assert a is False

    def test_true_expression(self):
        parser = self._get_parser('true and 1')
        result = parser.parse_and_expression()
        context = Context()
        visitor = ExecuteVisitor()
        a = visitor.visit_and_expression(result, context)
        assert a is True
    
    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)