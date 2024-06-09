from interpreter.parser.syntax_tree import *
from .interpreter import Context
from .interpreter_error import *
import numpy as np
import numbers
import sys, os
from .builtins import ImportedObject, built_in_functions

class ExecuteVisitor(Visitor):
    def __init__(self, recursion_limit=100):
        super().__init__()
        self.functions = built_in_functions.copy()
        self.includes = {}
        self.context_stack = [Context()]
        self.context = self.context_stack[-1] 
        self.last_result = None
        self.additional_args = None
        self.recursion_depth = 0
        self.recursion_limit = recursion_limit
        self.return_flag = False
        self.break_flag = False
    
    def increment_recursion_depth(self):
        if self.recursion_depth >= self.recursion_limit:
            raise RecursionLimitExceeded()
        self.recursion_depth += 1

    def decrement_recursion_depth(self):
        if self.recursion_depth > 0:
            self.recursion_depth -= 1
    
    def add_function(self, name, fun):
        self.functions[name] = fun

    def get_function(self, name):
        func = self.functions.get(name)
        return func
    
    def add_include(self, name, obj):
        self.includes[name] = obj

    def get_include(self, name):
        obj = self.includes.get(name)
        return obj
    
    def add_context(self):
        self.context_stack.append(self.context.new_context())
        self.context = self.context_stack[-1]
    
    def pop_context(self):
        self.context_stack.pop()
        self.context = self.context_stack[-1]

    def visit_program(self, element: Program):
        for function in element.functions:
            function = element.functions.get(function)
            self.add_function(function.name, function)
        for include in element.includes:
            include.accept(self)
        
        if 'main' not in self.functions:
            raise MainFunctionRequired()

    def visit_function_definition(self, element):
        args, method_name = self.additional_args
        if len(args) != len(element.parameters):
            raise ValueError(f"Expected {len(element.parameters)} arguments, got {len(args)} at postion: {element.position}")
        for arg, param in zip(args, element.parameters):
            self.context.add_variable(param, arg)
        element.statements.accept(self)
        self.return_flag = False

    def visit_include_statement(self, element: IncludeStatement):
        library_name = element.library_name
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        try:
            module = importlib.import_module(library_name)
            for obj_name in element.objects_names:
                if hasattr(module, obj_name):
                    obj = getattr(module, obj_name)
                    self.add_function(obj_name, ImportedObject(obj))
                else:
                    raise ImportError(f"Obiekt '{obj_name}' nie znaleziony w module '{library_name}'")
        except ImportError as e:
            raise ImportError(f"Nie można zaimportować: {str(e)}")

    def visit_lambda_expression(self, element: LambdaExpression):
        self.context.add_variable(element.variable_name, None)
        self.last_result = [element.variable_name, element.statements]

    def visit_function_arguments(self, element):
        args = []
        for arg in element.arguments:
            arg.accept(self)
            args.append(self.last_result)
        self.last_result = args

    def visit_identifier(self, element: Identifier):
        if element.parent is not None:
            element.parent.accept(self)
            self.last_result =  getattr(self.last_result, element.name)
        else:
            self.last_result = self.context.get_variable(element.name)

    def visit_parameter(self, element) :
        pass

    def visit_return_statement(self, element):
        if element.statement is not None:
            element.statement.accept(self)
        self.return_flag = True

    def visit_if_statement(self, element: IfStatement):
        element.condition.accept(self)
        if self.last_result:
            element.statements.accept(self)
        elif element.else_statement:
            element.else_statement.accept(self)

    def visit_while_statement(self, element: WhileStatement):
        self.context.while_flag += 1
        element.condition.accept(self)
        while self.last_result:
            self.context.reset_flags()
            element.condition.accept(self)
            if not self.last_result or self.break_flag:
                break
            element.statements.accept(self)
            if self.return_flag or self.break_flag:
                break
        self.break_flag = False
        self.context.while_flag -= 1
    
    def visit_break_statement(self, element: BreakStatement) :
        if self.context.while_flag == 0:
            raise RuntimeError(f"Break statement used outside of while loop at position: {element.position}")
        self.break_flag = True
        return

    def visit_or_expression(self, element: OrExpression) :
        element.nodes[0].accept(self)
        x = self.last_result
        if x:
            return
        for node in element.nodes[1:]:
            temp_cond = isinstance(x, np.ndarray)
            if (temp_cond and x.dtype == bool and x.all()) or (not temp_cond and x):
                self.last_result = True
                return
            
            node.accept(self)
            term = self.last_result
            if (temp_cond and x.dtype != bool) or \
                isinstance(term, np.ndarray) and term.dtype != bool:
                raise OrOperationError(x, term)
            elif isinstance(x, np.ndarray) and isinstance(term, np.ndarray):
                x = x | term
            elif not isinstance(x, numbers.Number) or not isinstance(term, numbers.Number):
                raise OrOperationError(x, term)
            else:
                x = bool(x) or bool(term)
        self.last_result = x

    def visit_and_expression(self, element: AndExpression) :
        element.nodes[0].accept(self)
        x = self.last_result
        if not x:
            return
        for node in element.nodes[1:]:
            temp_cond = isinstance(x, np.ndarray)
            if (temp_cond and x.dtype == bool and not x.all()) or (not temp_cond and not x):
                self.last_result = False
                return
            
            node.accept(self)
            term = self.last_result
            if (temp_cond and x.dtype != bool) or \
                isinstance(term, np.ndarray) and term.dtype != bool:
                raise AndOperationError(x, term)
            elif isinstance(x, np.ndarray) and isinstance(term, np.ndarray):
                x = x & term
            elif not isinstance(x, numbers.Number) or not isinstance(term, numbers.Number):
                raise AndOperationError(x, term)
            else:
                x = bool(x) and bool(term)
        self.last_result = x
    
    def visit_negation(self, element: Negation) :
        if element.negation_type == 'Logic':
            try:
                element.node.accept(self)
                self.last_result = not self.last_result
            except TypeError:
                raise TypeError(f"Invalid negation at position: {element.position}")
        elif element.negation_type == 'Arth':
            try:
                element.node.accept(self)
                self.last_result = - self.last_result
            except TypeError:
                raise TypeError(f"Invalid negation at position: {element.position}")

    def visit_sum_expression(self, element: SumExpression):
        element.left.accept(self)
        left_value = self.last_result
        element.right.accept(self)
        right_value = self.last_result
        self.last_result = self.try_sum(left_value, right_value, element.position)
    
    def try_sum(self, left_value, right_value, position):
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
            raise TypeError(f"Unsupported operand types for +: '{type(left_value).__name__}' and '{type(right_value).__name__}' at position: {position}")

    def visit_sub_expression(self, element: SubExpression):
        element.left.accept(self)
        left_value = self.last_result
        element.right.accept(self)
        right_value = self.last_result
        self.last_result = self.try_sub(left_value, right_value, element.position)
    
    def try_sub(self, left_value, right_value, position):
        if isinstance(left_value, (float, int)) and isinstance(right_value, (float, int))\
            or (isinstance(left_value, bool) and isinstance(right_value, bool)):
                return left_value - right_value
        else:
            raise TypeError(f"Unsupported operand types for -: '{type(left_value).__name__}' and '{type(right_value).__name__}' at position: {position}")

    def visit_mul_expression(self, element: MulExpression):
        element.left.accept(self)
        left_value = self.last_result
        element.right.accept(self)
        right_value = self.last_result
        self.last_result = self.try_mulitply(left_value, right_value, element.position)
    
    def try_mulitply(self, left_value, right_value, position):
        if isinstance(left_value, (float, int)) and isinstance(right_value, (float, int))\
            or (isinstance(left_value, int) and isinstance(right_value, str))\
            or (isinstance(left_value, str) and isinstance(right_value, int)):
                return left_value * right_value
        else:
            raise TypeError(f"Unsupported operand types for *: '{type(left_value).__name__}' and '{type(right_value).__name__}' at position: {position}")

    def visit_div_expression(self, element: DivExpression):
        element.left.accept(self)
        left_value = self.last_result
        element.right.accept(self)
        right_value = self.last_result
        if right_value == 0:
            raise ZeroDivisionError("Division by zero is not allowed")
        self.last_result = self.try_divide(left_value, right_value, element.position)
    
    def try_divide(self, left_value, right_value, position):
        if isinstance(left_value, (float, int)) and isinstance(right_value, (float, int)):
            return left_value / right_value
        else:
            raise TypeError(f"Unsupported operand types for *: '{type(left_value).__name__}' and '{type(right_value).__name__}' at position: {position}")

    def visit_equal_operation(self, element: EqualOperation):
        element.left.accept(self)
        left = self.last_result
        element.right.accept(self)
        right = self.last_result
        self.last_result = left == right

    def visit_not_equal_operation(self, element: NotEqualOperation) :
        element.left.accept(self)
        left = self.last_result
        element.right.accept(self)
        right = self.last_result
        self.last_result = left != right

    def visit_greater_operation(self, element: GreaterOperation) :
        element.left.accept(self)
        left = self.last_result
        element.right.accept(self)
        right = self.last_result
        self.last_result = left > right

    def visit_greater_equal_operation(self, element: GreaterEqualOperation) :
        element.left.accept(self)
        left = self.last_result
        element.right.accept(self)
        right = self.last_result
        self.last_result = left >= right

    def visit_less_operation(self, element: LessOperation):
        element.left.accept(self)
        left = self.last_result
        element.right.accept(self)
        right = self.last_result
        self.last_result = left < right

    def visit_less_equal_operation(self, element: LessEqualOperation):
        element.left.accept(self)
        left = self.last_result
        element.right.accept(self)
        right = self.last_result
        self.last_result = left <= right

    def visit_literal_bool(self, element: LiteralBool):
        self.last_result =  element.value

    def visit_literal_int(self, element: LiteralInt):
        self.last_result =  element.value

    def visit_literal_float(self, element: LiteralFloat):
        self.last_result =  element.value

    def visit_literal_string(self, element: LiteralString):
        self.last_result =  element.value

    def visit_array(self, element):
        value = []
        for item in element.items:
            item.accept(self)
            value.append(self.last_result)
        self.last_result = value

    def visit_assignment(self, element: Assignment):
        try:
            element.value.accept(self)
            value = self.last_result
            if element.target.parent:
                element.target.parent.accept(self)
                object = self.last_result
                setattr(object, element.target.name, value)
            else:
                self.context.add_variable(element.target.name, value)
        except AttributeError as e:
            raise AttributeError(f"Attribute error: {str(e)} at position: {element.position}")
        except Exception as e:
            raise RuntimeError(f"Error during assignment: {str(e)} at position: {element.position}")
    
    def visit_function_call(self, element: FunctionCall):
        try:
            self.increment_recursion_depth()
            if element.parent is not None:
                element.parent.accept(self)
                parent_value = self.last_result
            else:
                parent_value = None
            
            args = self.get_args(element, parent_value)
            
            if function := self.get_function(element.function_name):
                method_name = None 
            elif function := self.get_class_method(element):
                method_name = element.function_name
            
            if function is None:
                raise FunctionDoesNotExist(element.function_name)
            self.add_context()
            self.additional_args = (args, method_name)
            function.accept(self)
            self.pop_context()
        except RecursionLimitExceeded as e:
            raise e
        finally:
            self.decrement_recursion_depth()
    
    def get_args(self, element, parent_value):
        args = []
        element.arguments.accept(self)
        args = self.last_result
        if parent_value:
            args = [parent_value] + args
        return args
    
    def get_class_method(self, element):
        for obj in self.functions.values():
            if hasattr(obj, 'obj') and hasattr(obj.obj, element.function_name):
                return obj
        return None

    def visit_statements(self, element: Statements):
        for statement in element.statements:
            statement.accept(self)
            if self.return_flag or self.break_flag:
                break
    
    def visit_built_in_function(self, element):
        args, method_name = self.additional_args
        res =  element.function(*args)
        self.last_result = res
    
    def visit_imported_object(self, element):
        args, method_name = self.additional_args
        if method_name:
            method = getattr(element.obj, method_name, None)
            if method and callable(method):
                self.last_result = method(*args)
            else:
                raise AttributeError(f'Method {method_name} not found or not callable at position')
        else:
            if callable(element.obj):
                self.last_result = element.obj(*args)
            elif hasattr(element.obj, '__call__'):
                self.last_result = element.obj.__call__(*args)
            else:
                self.last_result = element.obj
    
    def visit_lambda_function(self, element):
        args, method_name = self.additional_args
        args = [self] + args
        res = element.function(*args)
        self.last_result = res