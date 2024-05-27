from interpreter.parser.syntax_tree import *
from .interpreter import Context
from .interpreter_error import *
import numpy as np
import numbers
import sys, os


class ExecuteVisitor(Visitor):
    def visit_program(self, element: Program, context: Context):
        for function in element.functions:
            function = element.functions.get(function)
            function.accept(self, context)
        for include in element.includes:
            include.accept(self, context)
        
        if 'main' not in context.functions:
            raise Exception()
        main_call = FunctionCall(SourcePosition(1, 1), 'main', FunctionArguments(SourcePosition(1, 1), []), None)
        ret_code = main_call.accept(self, context)
        if ret_code is None:
            ret_code = 0
        return ret_code

    def visit_function_definition(self, element, context: Context):
        context.add_function(element.name, element)

    def visit_include_statement(self, element: IncludeStatement, context: Context):
        library_name = element.library_name
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        try:
            module = importlib.import_module(library_name)
            for obj_name in element.objects_names:
                if hasattr(module, obj_name):
                    obj = getattr(module, obj_name)
                    context.add_include(obj_name, obj)
                else:
                    raise ImportError(f"Obiekt '{obj_name}' nie znaleziony w module '{library_name}'")
        except ImportError as e:
            raise ImportError(f"Nie można zaimportować: {str(e)}")

    def visit_lambda_expression(self, element: LambdaExpression, context: Context):
        context.add_variable(element.variable_name, None)
        return element.variable_name

    def visit_function_arguments(self, element, context: Context):
        args = [arg.accept(self, context) for arg in element.arguments]
        return args

    def visit_identifier(self, element: Identifier, context: Context):
        if element.parent is not None:
            parent_value = element.parent.accept(self, context)
            return getattr(parent_value, element.name)
        else:
            return context.get_variable(element.name)

    def visit_parameter(self, element, context) :
        pass

    def visit_return_statement(self, element, context: Context) :
        return element.statement.accept(self, context)

    def visit_if_statement(self, element: IfStatement, context: Context) :
        if element.condition.accept(self, context):
            return element.statements.accept(self, context)
        elif element.else_statement:
            return element.else_statement.accept(self, context)

    def visit_while_statement(self, element: WhileStatement, context: Context) :
        try:
            while element.condition.accept(self, context):
                try:
                    if ret := element.statements.accept(self, context):
                        return ret
                except BreakException:
                    break
        except BreakException:
            pass

    def visit_break_statement(self, element, context) :
        raise BreakException()

    def visit_or_expression(self, element: OrExpression, context) :
        x = element.nodes[0].accept(self, context)
        for node in element.nodes[1:]:
            temp_cond = isinstance(x, np.ndarray)
            if (temp_cond and x.dtype == bool and x.all()) or (not temp_cond and x):
                return True
            
            term = node.accept(self, context)
            if (temp_cond and x.dtype != bool) or \
                isinstance(term, np.ndarray) and term.dtype != bool:
                raise OrOperationError(x, term)
            elif isinstance(x, np.ndarray) and isinstance(term, np.ndarray):
                x = x | term
            elif not isinstance(x, numbers.Number) or not isinstance(term, numbers.Number):
                raise OrOperationError(x, term)
            else:
                x = bool(x) or bool(term)
        return x

    def visit_and_expression(self, element: AndExpression, context: Context) :
        x = element.nodes[0].accept(self, context)
        for node in element.nodes[1:]:
            temp_cond = isinstance(x, np.ndarray)
            if (temp_cond and x.dtype == bool and not x.all()) or (not temp_cond and not x):
                return False
            
            term = node.accept(self, context)
            if (temp_cond and x.dtype != bool) or \
                isinstance(term, np.ndarray) and term.dtype != bool:
                raise AndOperationError(x, term)
            elif isinstance(x, np.ndarray) and isinstance(term, np.ndarray):
                x = x & term
            elif not isinstance(x, numbers.Number) or not isinstance(term, numbers.Number):
                raise AndOperationError(x, term)
            else:
                x = bool(x) and bool(term)
        return x
    
    def visit_negation(self, element: Negation, context: Context) :
        if element.negation_type == 'Logic':
            try:
                return not element.node.accept(self, context)
            except TypeError:
                raise TypeError()
        elif element.negation_type == 'Arth':
            try:
                return - element.node.accept(self, context)
            except TypeError:
                raise TypeError()

    def visit_sum_expression(self, element: SumExpression, context:Context):
        left_value = element.left.accept(self, context)
        right_value = element.right.accept(self, context)
        return self.check_sum_types(left_value, right_value)
    
    def check_sum_types(self, left_value, right_value):
        if isinstance(left_value, int) and isinstance(right_value, int):
            return left_value + right_value
        if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            return float(left_value) + float(right_value)
        elif isinstance(left_value, (int, float)) and isinstance(right_value, str):
            return str(left_value) + str(right_value)
        elif isinstance(left_value, str) and isinstance(right_value, (int, float)):
            return left_value + str(right_value)
        elif type(left_value) == type(right_value):
            return left_value + right_value
        else:
            raise TypeError(f"Unsupported operand types for +: '{type(left_value).__name__}' and '{type(right_value).__name__}'")

    def visit_sub_expression(self, element: SubExpression, context: Context):
        left_value = element.left.accept(self, context)
        right_value = element.right.accept(self, context)
        return self.check_sub_types(left_value, right_value)
    
    def check_sub_types(self, left_value, right_value):
        if isinstance(left_value, (float, int)) and isinstance(right_value, (float, int))\
            or (isinstance(left_value, bool) and isinstance(right_value, bool)):
                return left_value - right_value
        else:
            raise TypeError(f"Unsupported operand types for -: '{type(left_value).__name__}' and '{type(right_value).__name__}'")

    def visit_mul_expression(self, element: MulExpression, context: Context):
        left_value = element.left.accept(self, context)
        right_value = element.right.accept(self, context)
        return self.check_mul_types(left_value, right_value)
    
    def check_mul_types(self, left_value, right_value):
        if isinstance(left_value, (float, int)) and isinstance(right_value, (float, int))\
            or (isinstance(left_value, int) and isinstance(right_value, str))\
            or (isinstance(left_value, str) and isinstance(right_value, int)):
                return left_value * right_value
        else:
            raise TypeError(f"Unsupported operand types for *: '{type(left_value).__name__}' and '{type(right_value).__name__}'")

    def visit_div_expression(self, element: DivExpression, context: Context):
        left_value = element.left.accept(self, context)
        right_value = element.right.accept(self, context)
        if right_value == 0:
            raise ZeroDivisionError("Division by zero is not allowed")
        return self.check_div_types(left_value, right_value)
    
    def check_div_types(self, left_value, right_value):
        if isinstance(left_value, (float, int)) and isinstance(right_value, (float, int)):
            return left_value / right_value
        else:
            raise TypeError(f"Unsupported operand types for *: '{type(left_value).__name__}' and '{type(right_value).__name__}'")

    def visit_equal_operation(self, element: EqualOperation, context: Context) :
        return element.left.accept(self, context) == element.right.accept(self, context)

    def visit_not_equal_operation(self, element: NotEqualOperation, context: Context) :
        return element.left.accept(self, context) != element.right.accept(self, context)

    def visit_greater_operation(self, element: GreaterOperation, context: Context) :
        return element.left.accept(self, context) > element.right.accept(self, context)

    def visit_greater_equal_operation(self, element: GreaterEqualOperation, context: Context) :
        return element.left.accept(self, context) >= element.right.accept(self, context)

    def visit_less_operation(self, element: LessOperation, context: Context):
        return element.left.accept(self, context) < element.right.accept(self, context)

    def visit_less_equal_operation(self, element: LessEqualOperation, context: Context):
        return element.left.accept(self, context) <= element.right.accept(self, context)

    def visit_literal_bool(self, element: LiteralBool, context):
        return element.value

    def visit_literal_int(self, element: LiteralInt, context):
        return element.value

    def visit_literal_float(self, element: LiteralFloat, context):
        return element.value

    def visit_literal_string(self, element: LiteralString, context):
        return element.value

    def visit_array(self, element, context):
        value = []
        for item in element.items:
            value.append(item.accept(self, context))
        return value

    def visit_assignment(self, element: Assignment, context: Context):
        try:
            value = element.value.accept(self, context)
            if element.target.parent:
                object = element.target.parent.accept(self, context)
                setattr(object, element.target.name, value)
            else:
                context.add_variable(element.target.name, value)
        except AttributeError as e:
            raise AttributeError(f"Attribute error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error during assignment: {str(e)}")
    
    def visit_function_call(self, element: FunctionCall, context: Context):
        try:
            context.increment_recursion_depth()
            if element.parent is not None:
                parent_value = element.parent.accept(self, context)

                if isinstance(parent_value, list):
                    function = context.functions.get(element.function_name)
                    if not function:
                        raise FunctionDoesNotExist(element.function_name)
                else:
                    function = getattr(parent_value, element.function_name, None)
                    if function is None:
                        raise FunctionDoesNotExist(element.function_name)
            else:
                function = context.get_function(element.function_name) or self.get_class_method(element, context) or self.get_constructor(element, context)
                if function is None:
                    raise FunctionDoesNotExist(element.function_name)

            if hasattr(element.arguments, "arguments"):
                args = [arg.accept(self, context) for arg in element.arguments.arguments]
            elif hasattr(element.arguments, "variable_name"):
                args = element.arguments.accept(self, context)

            if isinstance(function, FunctionDefintion):
                function_context = context.new_context()
                reference_args = []
                for arg, param in zip(args, function.parameters):
                    if isinstance(arg, list):
                        reference_args.append(param)
                    function_context.add_variable(param, arg)
                ret = function.statements.accept(self, function_context)
                for arg in reference_args:
                    context.add_variable(arg, function_context.get_variable(arg))
                return ret
            else:
                if element.parent is not None and isinstance(parent_value, list):
                    if element.function_name in context.lambda_funtions:
                        return function(parent_value, element.arguments.statements, self, context, args)
                    return function(parent_value, *args)
                else:
                    return function(*args)
        except RecursionLimitExceeded as e:
            raise e
        finally:
            context.decrement_recursion_depth()
    
    def get_class_method(self, element, context):
        for obj in context.includes.values():
            if function := getattr(obj, element.function_name, None):
                return function
        return None
    
    def get_constructor(self, element, context):       
        for class_name, cls in context.includes.items():
            if class_name == element.function_name:
                return cls
        return None

    def visit_statements(self, element: Statements, context):
            for statement in element.statements:
                ret = statement.accept(self, context)
                if ret:
                    return ret