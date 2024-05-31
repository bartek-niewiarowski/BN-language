import io
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.parser.parser import Parser
from interpreter.parser.syntax_error import *
from interpreter.parser.syntax_tree import *
from interpreter.interpreter.executeVisitor import ExecuteVisitor
from interpreter.interpreter.interpreter import Context, Interpreter
from interpreter.interpreter.interpreter_error import *

class TestInterpreter:
    def test_false_and_expression(self):
        parser = self._get_parser('true and false')
        result = parser.parse_and_expression()
        context = Context()
        visitor = ExecuteVisitor()
        visitor.visit_and_expression(result, context)
        assert context.last_result is False

    def test_true_and_expression(self):
        parser = self._get_parser('true and true')
        result = parser.parse_and_expression()
        context = Context()
        visitor = ExecuteVisitor()
        visitor.visit_and_expression(result, context)
        assert context.last_result is True
    
    def test_true_and_expression_with_int(self):
        parser = self._get_parser('true and 1')
        result = parser.parse_and_expression()
        context = Context()
        visitor = ExecuteVisitor()
        visitor.visit_and_expression(result, context)
        assert context.last_result is True
    
    def test_true_or_expression(self):
        parser = self._get_parser('true or false')
        result = parser.parse_or_expression()
        context = Context()
        visitor = ExecuteVisitor()
        visitor.visit_or_expression(result, context)
        assert context.last_result is True
    
    def test_false_or_expression(self):
        parser = self._get_parser('false or false')
        result = parser.parse_or_expression()
        context = Context()
        visitor = ExecuteVisitor()
        visitor.visit_or_expression(result, context)
        assert context.last_result is False
    
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
            visitor.visit_sum_expression(result, context)
            results.append(context.last_result)
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
            visitor.visit_sub_expression(result, context)
            results.append(context.last_result)
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
            visitor.visit_mul_expression(result, context)
            results.append(context.last_result)
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
            visitor.visit_div_expression(result, context)
            results.append(context.last_result)
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
            visitor.visit_equal_operation(result, context)
            results.append(context.last_result)
        assert results == [True, True, False, True, False, True, False]

    def test_comparison_not_equal(self):
        expressions = ["1 != 2", "1.5 != 2.5", "2 != 1", "2 != 2", "true != true", 
                       "true != false", "[1] != [1]", "[1] != [2]", '"a" != "b"']
        results = []
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_logic_expression()
            visitor.visit_not_equal_operation(result, context)
            results.append(context.last_result)
        assert results == [True, True, True, False, False, True, False, True, True]

    def test_comparison_greater(self):
        expressions = ["1 > 2", "1.5 > 2.5", "2 > 1", "2 > 2", "true > true", '"a" > "b"']
        results = []
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_logic_expression()
            visitor.visit_greater_operation(result, context)
            results.append(context.last_result)
        assert results == [False, False, True, False, False, False]

    def test_comparison_greater_equal(self):
        expressions = ["1 >= 2", "1.5 >= 2.5", "2 >= 1", "2 >= 2", "true >= true", '"a" >= "b"']
        results = []
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_logic_expression()
            visitor.visit_greater_equal_operation(result, context)
            results.append(context.last_result)
        assert results == [False, False, True, True, True, False]

    def test_comparison_less(self):
        expressions = ["1 < 2", "1.5 < 2.5", "2 < 1", "2 < 2", "true < true", '"a" < "b"']
        results = []
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_logic_expression()
            visitor.visit_less_operation(result, context)
            results.append(context.last_result)
        assert results == [True, True, False, False, False, True]

    def test_comparison_less_equal(self):
        expressions = ["1 <= 2", "1.5 <= 2.5", "2 <= 1", "2 <= 2", "true <= true", '"a" <= "b"']
        results = []
        context = Context()
        visitor = ExecuteVisitor()
        for expression in expressions:
            parser = self._get_parser(expression)
            result = parser.parse_logic_expression()
            visitor.visit_less_equal_operation(result, context)
            results.append(context.last_result)
        assert results == [True, True, False, True, True, True]        
    
    def test_program(self):
        parser = self._get_parser('def main() {x=5;\nreturn x;}\n')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == 5
    
    def test_includes(self):
        parser = self._get_parser('from student import Student; def main() {s = Student("Adam", 22); return [s.name, s.age];}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == ["Adam", 22]
    
    def test_include_assignment(self):
        parser = self._get_parser('from student import Student; def main() {s = Student("Adam", 22); b = s.age; return b;}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == 22

    def test_include_change_field_value(self):
        parser = self._get_parser('from student import Student; def main() {s = Student("Adam", 22); s.age = 23; return s.age;}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == 23

    def test_include_call_method(self):
        parser = self._get_parser('from student import Student; def main() {s = Student("Adam", 22); return s.greet();}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == "Hello, my name is Adam and I am 22 years old."
    
    def test_include_call_method_many_classes(self):
        parser = self._get_parser("""from student import Student, Class; 
                                  def main() 
                                  {s = Student("Adam", 22); 
                                  class = Class(35, "Koc"); 
                                  a = class.getTeacher(); 
                                  b = class.getStudents(); 
                                  class.setStudents(40); 
                                  class.setTeacher("Nowak"); 
                                  return [a, b, class.getTeacher(), class.getStudents()];}""")
            
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == ["Koc", 35, "Nowak", 40]

    def test_array_append(self):
        parser = self._get_parser('def main() {lst = [1, 2, 3];\n lst.append(4);\n return lst;}\n')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == [1, 2, 3, 4]
    
    def test_array_remove(self):
        parser = self._get_parser('def main() {lst = [1, 2, 3];\n lst.remove(2);\n return lst;}\n')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == [1, 2]

    def test_array_get(self):
        parser = self._get_parser('def main() {lst = [1, 2, 3];\n lst.append(4);\n return lst.get(0);}\n')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == 1
    
    def test_while(self):
        parser = self._get_parser('def main() {a = 0; while(a <= 5) {a = a + 1;} return a;}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == 6
    
    def test_if(self):
        parser = self._get_parser('def main() {a = 5; if(a >= 0) {return a;} else {return 1;}}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        assert interpreter.execute(visitor) == 5
    
    def test_if_else(self):
        parser = self._get_parser('def main() {a = 5; if(a >= 6) {return a;} else {return 1;}}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == 1
    
    def test_lambda_foreach(self):
        parser = self._get_parser('def main() {a = [1, 2, 3]; b = a.foreach($x => { x = x + 1; }); return b;}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == [2, 3, 4]
    
    def test_lambda_foreach_many_stms(self):
        parser = self._get_parser('def main() {a = [1, 2, 3]; b = a.foreach($x => { y = x + 1; y = y * y; x = y; }); return b;}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == [4, 9, 16]

    # do konsultacji
    def test_lambda_where(self):
        parser = self._get_parser('def main() {a = [1, 2, 3]; b = a.where($x => { (x > 1) }); return b;}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == [2, 3]
    
    def test_negation_arth(self):
        parser = self._get_parser('def main() {a = 42; return -a;}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == -42
    
    def test_negation_logic(self):
        programs = [
            'def main() {a = "42"; return !a;}',
            'def main() {a = [42, 43, 35]; return !a;}',
            'from student import Student; def main() {a = Student(1, 2); return !a;}',
            'def main() {a = true; return !a;}',
            'def main() {a = false; return !a;}'
        ]
        returns = []
        for program in programs:
            parser = self._get_parser(program)
            interpreter = Interpreter(parser.parse_program())
            visitor = ExecuteVisitor()
            ret = interpreter.execute(visitor)
            returns.append(ret)
        assert returns == [False, False, False, False, True]
    
    def test_negation_arth_throw_error(self):
        programs = [
            'def main() {a = "42"; return -a;}',
            'def main() {a = [42, 43, 35]; return -a;}',
            'from student import Student; def main() {a = Student(1, 2); return -a;}'
        ]
        for program in programs:
            parser = self._get_parser(program)
            interpreter = Interpreter(parser.parse_program())
            visitor = ExecuteVisitor()
            with pytest.raises(TypeError):
                interpreter.execute(visitor)
    
    def test_recursion_within_limit(self):
        parser = self._get_parser('def factorial(n) {if (n <= 1) {return 1;} else {return n * factorial(n - 1);}} def main() {return factorial(5);}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == 120

    def test_recursion_exceeds_limit(self):
        parser = self._get_parser('def infiniteRecursion(n) {n = n + 1; print(n); return infiniteRecursion(n + 1);} def main() {return infiniteRecursion(1);}')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        with pytest.raises(RecursionLimitExceeded):
            interpreter.execute(visitor)
    
    def test_no_reference_args(self):
        parser = self._get_parser('def increment(x) {x = x + 1;} def main() {x = 5; increment(x); return x;}\n')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == 5
    
    def test_reference_args(self):
        parser = self._get_parser('def setZero(x) {x = [0];} def main() {x = [5]; setZero(x); return x;}\n')
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == [0]
    
    def test_program_4(self):
        parser = self._get_parser("""def increment(x) {
                                        x = x + 1;
                                        return x;
                                    }

                                    def main() {
                                        x = 5;
                                        print(x);
                                        x = increment(x);
                                        print(x);
                                    }""")
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == 0
    
    def test_break(self):
        parser = self._get_parser("""
                                    def main() {
                                        x = 5;
                                        if(x > 1) {
                                            break;
                                            x = 6;
                                        }
                                        return x;
                                    }""")
        interpreter = Interpreter(parser.parse_program())
        visitor = ExecuteVisitor()
        ret = interpreter.execute(visitor)
        assert ret == 5

    @staticmethod
    def _get_parser(string: str) -> Parser:
        src = Source(io.StringIO(string))
        lexer = Lexer(src)
        return Parser(lexer)