from .builtins import built_in_functions
from .interpreter_error import *
from ..parser.syntax_tree import FunctionCall, FunctionArguments

class Context:
    def __init__(self, recursion_limit = 100):
        self.variables = {}
        self.recursion_depth = 0
        self.recursion_limit = recursion_limit
        self.last_result = None
        self.return_flag = False
        self.break_flag = False
        self.reference_args = []
    
    def reset_flags(self):
        self.return_flag = False
        self.break_flag = False
    
    def add_reference(self, arg, param):
        if isinstance(arg, list):
            self.reference_args.append(param)
    
    def reset_reference(self):
        self.reference_args = []

    def add_variable(self, name, value):
        self.variables[name] = value

    def get_variable(self, name):
        if name not in self.variables:
            raise KeyError(f"Variable '{name}' is not defined.")
        return self.variables.get(name)
    
    def increment_recursion_depth(self):
        if self.recursion_depth >= self.recursion_limit:
            raise RecursionLimitExceeded()
        self.recursion_depth += 1

    def decrement_recursion_depth(self):
        if self.recursion_depth > 0:
            self.recursion_depth -= 1

    def new_context(self):
        new_context = Context(self.recursion_limit)
        new_context.recursion_depth = self.recursion_depth
        return new_context


class Interpreter:
    def __init__(self, program):
        self.program = program

    def execute(self, visitor):
        self.program.accept(visitor)
        main_call = FunctionCall(visitor.functions.get('main').position, 'main', FunctionArguments(visitor.functions.get('main').position, []))
        main_call.accept(visitor)
        ret_code = visitor.last_result if visitor.last_result is not None else 0
        return ret_code
