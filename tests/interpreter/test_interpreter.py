import io
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.parser.parser import Parser
from interpreter.parser.syntax_error import *
from interpreter.parser.syntax_tree import *
from interpreter.interpreter.executeVisitor import ExecuteVisitor
from interpreter.interpreter.interpreter import Context, Interpreter

class TestInterpreter:
    def test_false_and_expression(self):
        parser = self._get_parser('true and false')
        result = parser.parse_and_expression()
        context = Context()
        visitor = ExecuteVisitor()
        a = visitor.visit_and_expression(result, context)
        assert a is False

    def test_true_and_expression(self):
        parser = self._get_parser('true and true')
        result = parser.parse_and_expression()
        context = Context()
        visitor = ExecuteVisitor()
        a = visitor.visit_and_expression(result, context)
        assert a is True
    
    def test_true_and_expression_with_int(self):
        parser = self._get_parser('true and 1')
        result = parser.parse_and_expression()
        context = Context()
        visitor = ExecuteVisitor()
        a = visitor.visit_and_expression(result, context)
        assert a is True
    
    def test_true_or_expression(self):
        parser = self._get_parser('true or false')
        result = parser.parse_or_expression()
        context = Context()
        visitor = ExecuteVisitor()
        a = visitor.visit_or_expression(result, context)
        assert a is True
    
    def test_false_or_expression(self):
        parser = self._get_parser('false or false')
        result = parser.parse_or_expression()
        context = Context()
        visitor = ExecuteVisitor()
        a = visitor.visit_or_expression(result, context)
        assert a is False
    
    def test_assignment(self):
        parser = self._get_parser('x = 5;')
        result = parser.parse_function_call_or_assignment()
        context = Context()
        visitor = ExecuteVisitor()
        visitor.visit_assignment(result, context)
        assert context.get_variable('x') == 5
    
    def test_comparison_equal(self):
        expressions = ["1 == 1", "1.5 == 1.5", "2 == 1", "true == true", 
                       "true == false", "[1] == [1]", "[1] == [2]"]
        results = []
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_logic_expression()
            results.append(visitor.visit_equal_operation(result, context))
        assert results == [True, True, False, True, False, True, False]
    
    def test_program(self):
        parser = self._get_parser('def main() {x=5;\nreturn x;}\n')
        result = parser.parse_program()
        visitor = ExecuteVisitor()
        interpreter = Interpreter(result) 
        a = interpreter.execute(visitor)
        pass

    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)