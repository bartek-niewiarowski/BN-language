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
    
    def test_sum(self):
        expressions = ["1 + 1", "1.5 + 1.5", "2 + 1.5", '"true" + 2', '"true" + 2.5','"true" + " false"', "1+1+1+1+1", "true + false", "[1, 2] + [3, 4]"]
        results = []
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_arth_expression()
            results.append(visitor.visit_sum_expression(result, context))
        assert results == [2, 3.0, 3.5, "true2", "true2.5", "true false", 5, 1, [1, 2, 3, 4]]
    
    def test_sum_invalid_types(self):
        expressions = ['[1, 2, 3] + "abc"', '[1, 2, 3] + false']
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_arth_expression()
            with pytest.raises(TypeError):
                visitor.visit_sum_expression(result, context)\

    def test_sub(self):
        expressions = ["1 - 1", "1.5 - 1.5", "2 - 1.5", "true - false", "1-2"]
        results = []
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_arth_expression()
            results.append(visitor.visit_sub_expression(result, context))
        assert results == [0, 0, 0.5, 1, -1]
    
    def test_sub_invalid_types(self):
        expressions = ['[1, 2, 3] - "abc"', '[1, 2, 3] - false', '"bav" - "ghg"', '[1, 2, 3] - [1, 2]', '1 - "a"']
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_arth_expression()
            with pytest.raises(TypeError):
                visitor.visit_sub_expression(result, context)

    def test_mul(self):
        expressions = ["1 * 1", "1.5 * 1.5", "2 * 1.5", '3 * "a"','true * "abc"']
        results = []
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_arth_expression()
            results.append(visitor.visit_mul_expression(result, context))
        assert results == [1, 2.25, 3.0, "aaa", "abc"]

    def test_mul_invalid_types(self):
        expressions = ['"abc" * "abc"', '[1, 2, 3] * true', '1 * [1, 2, 3], ']
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_arth_expression()
            with pytest.raises(TypeError):
                visitor.visit_mul_expression(result, context)
    
    def test_div(self):
        expressions = ["1 / 1", "1.5 / 1.5", "2 / 1.0"]
        results = []
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_arth_expression()
            results.append(visitor.visit_div_expression(result, context))
        assert results == [1, 1, 2.0]

    def test_div_invalid_types(self):
        expressions = ['"abc" / "abc"', '[1, 2, 3] / true', '1 / [1, 2, 3], ']
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_arth_expression()
            with pytest.raises(TypeError):
                visitor.visit_div_expression(result, context)
    
    def test_div_by_zero(self):
        expressions = ['1/0', '1/(2-2)', '1/1*0']
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_arth_expression()
            with pytest.raises(ZeroDivisionError):
                visitor.visit_div_expression(result, context)
    
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
        a = visitor.visit_program(result, Context())
        assert a == 5
    
    def test_includes(self):
        parser = self._get_parser('from student import Student; def main() {s = Student(1, 10);\n return s.age;}\n')
        result = parser.parse_program()
        visitor = ExecuteVisitor()
        a = visitor.visit_program(result, Context())
        assert a == 5

    def test_array_append(self):
        parser = self._get_parser('def main() {lst = [1, 2, 3];\n lst.append(4);\n return lst;}\n')
        result = parser.parse_program()
        visitor = ExecuteVisitor()
        ret = visitor.visit_program(result, Context())
        assert ret == [1, 2, 3, 4]
    
    def test_array_remove(self):
        parser = self._get_parser('def main() {lst = [1, 2, 3];\n lst.remove(2);\n return lst;}\n')
        result = parser.parse_program()
        visitor = ExecuteVisitor()
        ret = visitor.visit_program(result, Context())
        assert ret == [1, 2]

    def test_array_get(self):
        parser = self._get_parser('def main() {lst = [1, 2, 3];\n lst.append(4);\n return lst.get(0);}\n')
        result = parser.parse_program()
        visitor = ExecuteVisitor()
        ret = visitor.visit_program(result, Context())
        assert ret == 1

    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)