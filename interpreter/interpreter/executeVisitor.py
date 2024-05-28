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
            raise MainFunctionRequired()
        #main_call = FunctionCall(SourcePosition(1, 1), 'main', None), None)
        main_call = FunctionCall(context.functions.get('main').position, 'main', FunctionArguments(context.functions.get('main').position, []))
        main_call.accept(self, context)
        ret_code = context.last_result if context.last_result is not None else 0
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
        context.last_result = element.variable_name

    def visit_function_arguments(self, element, context: Context):
        context.last_result = [arg.accept(self, context) for arg in element.arguments]

    def visit_identifier(self, element: Identifier, context: Context):
        if element.parent is not None:
            element.parent.accept(self, context)
            context.last_result =  getattr(context.last_result, element.name)
        else:
            context.last_result = context.get_variable(element.name)

    def visit_parameter(self, element, context) :
        pass

    def visit_return_statement(self, element, context: Context):
        element.statement.accept(self, context)
        context.return_flag = True

    def visit_if_statement(self, element: IfStatement, context: Context):
        element.condition.accept(self, context)
        if context.last_result:
            element.statements.accept(self, context)
        elif element.else_statement:
            element.else_statement.accept(self, context)

    def visit_while_statement(self, element: WhileStatement, context: Context) :
        while True:
            context.reset_flags()
            element.condition.accept(self, context)
            if not context.last_result or context.break_flag:
                break

            element.statements.accept(self, context)
            if context.return_flag or context.break_flag:
                break
    
    def visit_break_statement(self, element, context: Context) :
        context.break_flag = True
        return

    def visit_or_expression(self, element: OrExpression, context: Context) :
        element.nodes[0].accept(self, context)
        x = context.last_result
        for node in element.nodes[1:]:
            temp_cond = isinstance(x, np.ndarray)
            if (temp_cond and x.dtype == bool and x.all()) or (not temp_cond and x):
                return True
            
            node.accept(self, context)
            term = context.last_result6
            if (temp_cond and x.dtype != bool) or \
                isinstance(term, np.ndarray) and term.dtype != bool:
                raise OrOperationError(x, term)
            elif isinstance(x, np.ndarray) and isinstance(term, np.ndarray):
                x = x | term
            elif not isinstance(x, numbers.Number) or not isinstance(term, numbers.Number):
                raise OrOperationError(x, term)
            else:
                x = bool(x) or bool(term)
        context.last_result = x

    def visit_and_expression(self, element: AndExpression, context: Context) :
        element.nodes[0].accept(self, context)
        x = context.last_result
        for node in element.nodes[1:]:
            temp_cond = isinstance(x, np.ndarray)
            if (temp_cond and x.dtype == bool and not x.all()) or (not temp_cond and not x):
                return False
            
            node.accept(self, context)
            term = context.last_result
            if (temp_cond and x.dtype != bool) or \
                isinstance(term, np.ndarray) and term.dtype != bool:
                raise AndOperationError(x, term)
            elif isinstance(x, np.ndarray) and isinstance(term, np.ndarray):
                x = x & term
            elif not isinstance(x, numbers.Number) or not isinstance(term, numbers.Number):
                raise AndOperationError(x, term)
            else:
                x = bool(x) and bool(term)
        context.last_result = x
    
    def visit_negation(self, element: Negation, context: Context) :
        if element.negation_type == 'Logic':
            try:
                element.node.accept(self, context)
                context.last_result = not context.last_result
            except TypeError:
                raise TypeError()
        elif element.negation_type == 'Arth':
            try:
                element.node.accept(self, context)
                context.last_result = - context.last_result
            except TypeError:
                raise TypeError()

    def visit_sum_expression(self, element: SumExpression, context:Context):
        element.left.accept(self, context)
        left_value = context.last_result
        element.right.accept(self, context)
        right_value = context.last_result
        context.last_result = self.check_sum_types(left_value, right_value)
    
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
        element.left.accept(self, context)
        left_value = context.last_result
        element.right.accept(self, context)
        right_value = context.last_result
        context.last_result = self.check_sub_types(left_value, right_value)
    
    def check_sub_types(self, left_value, right_value):
        if isinstance(left_value, (float, int)) and isinstance(right_value, (float, int))\
            or (isinstance(left_value, bool) and isinstance(right_value, bool)):
                return left_value - right_value
        else:
            raise TypeError(f"Unsupported operand types for -: '{type(left_value).__name__}' and '{type(right_value).__name__}'")

    def visit_mul_expression(self, element: MulExpression, context: Context):
        element.left.accept(self, context)
        left_value = context.last_result
        element.right.accept(self, context)
        right_value = context.last_result
        context.last_result = self.check_mul_types(left_value, right_value)
    
    def check_mul_types(self, left_value, right_value):
        if isinstance(left_value, (float, int)) and isinstance(right_value, (float, int))\
            or (isinstance(left_value, int) and isinstance(right_value, str))\
            or (isinstance(left_value, str) and isinstance(right_value, int)):
                return left_value * right_value
        else:
            raise TypeError(f"Unsupported operand types for *: '{type(left_value).__name__}' and '{type(right_value).__name__}'")

    def visit_div_expression(self, element: DivExpression, context: Context):
        element.left.accept(self, context)
        left_value = context.last_result
        element.right.accept(self, context)
        right_value = context.last_result
        if right_value == 0:
            raise ZeroDivisionError("Division by zero is not allowed")
        context.last_result = self.check_div_types(left_value, right_value)
    
    def check_div_types(self, left_value, right_value):
        if isinstance(left_value, (float, int)) and isinstance(right_value, (float, int)):
            return left_value / right_value
        else:
            raise TypeError(f"Unsupported operand types for *: '{type(left_value).__name__}' and '{type(right_value).__name__}'")

    def visit_equal_operation(self, element: EqualOperation, context: Context):
        element.left.accept(self, context)
        left = context.last_result
        element.right.accept(self, context)
        right = context.last_result
        context.last_result = left == right

    def visit_not_equal_operation(self, element: NotEqualOperation, context: Context) :
        element.left.accept(self, context)
        left = context.last_result
        element.right.accept(self, context)
        right = context.last_result
        context.last_result = left != right

    def visit_greater_operation(self, element: GreaterOperation, context: Context) :
        element.left.accept(self, context)
        left = context.last_result
        element.right.accept(self, context)
        right = context.last_result
        context.last_result = left > right

    def visit_greater_equal_operation(self, element: GreaterEqualOperation, context: Context) :
        element.left.accept(self, context)
        left = context.last_result
        element.right.accept(self, context)
        right = context.last_result
        context.last_result = left >= right

    def visit_less_operation(self, element: LessOperation, context: Context):
        element.left.accept(self, context)
        left = context.last_result
        element.right.accept(self, context)
        right = context.last_result
        context.last_result = left < right

    def visit_less_equal_operation(self, element: LessEqualOperation, context: Context):
        element.left.accept(self, context)
        left = context.last_result
        element.right.accept(self, context)
        right = context.last_result
        context.last_result = left <= right

    def visit_literal_bool(self, element: LiteralBool, context: Context):
        context.last_result =  element.value

    def visit_literal_int(self, element: LiteralInt, context: Context):
        context.last_result =  element.value

    def visit_literal_float(self, element: LiteralFloat, context: Context):
        context.last_result =  element.value

    def visit_literal_string(self, element: LiteralString, context: Context):
        context.last_result =  element.value
    # opakowanie w obiekt literałów, plus opakowanie obiektu w ObjectValue - do zastanowienia

    def visit_array(self, element, context: Context):
        value = []
        for item in element.items:
            item.accept(self, context)
            value.append(context.last_result)
        context.last_result = value

    def visit_assignment(self, element: Assignment, context: Context):
        # opakowanie wartosci w obiekcie
        try:
            element.value.accept(self, context)
            value = context.last_result
            if element.target.parent:
                element.target.parent.accept(self, context)
                object = context.last_result
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
                element.parent.accept(self, context)
                parent_value = context.last_result

                # obiekt opakowujący obiekt listy i innych wartości
                # po opakowaniu jednolita obsługa wszystkiego
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
            # w function call tylko przygotowanie args, bez powiazania
            if hasattr(element.arguments, "arguments"):
                args = []
                for arg in element.arguments.arguments:
                    arg.accept(self, context)
                    args.append(context.last_result)
            elif hasattr(element.arguments, "variable_name"):
                element.arguments.accept(self, context)
                args = context.last_result

            if isinstance(function, FunctionDefintion):
                # czy nie powinno to byc w functionDefinition? poniezej odwiedzenie obiektu
                function_context = context.new_context()
                reference_args = []
                for arg, param in zip(args, function.parameters):
                    if isinstance(arg, list):
                        reference_args.append(param)
                    function_context.add_variable(param, arg)
                function.statements.accept(self, function_context)
                context.last_result = function_context.last_result
                for arg in reference_args:
                    context.add_variable(arg, function_context.get_variable(arg))
            else:
                if element.parent is not None and isinstance(parent_value, list):
                    if element.function_name in context.lambda_funtions:
                        context.last_result = function(parent_value, element.arguments.statements, self, context, args)
                        return
                    context.last_result = function(parent_value, *args)
                    return
                else:
                    context.last_result = function(*args)
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
        # przy include dodanie konstruktora do moich funkcjach       
        for class_name, cls in context.includes.items():
            if class_name == element.function_name:
                return cls
        return None

    def visit_statements(self, element: Statements, context):
        for statement in element.statements:
            statement.accept(self, context)
            if context.return_flag or context.break_flag:
                # If a return or break was executed, stop processing more statements
                break