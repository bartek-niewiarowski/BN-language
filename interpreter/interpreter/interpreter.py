from .builtins import built_in_functions, lambda_functions
from .interpreter_error import *
import copy

class Context:
    def __init__(self, recursion_limit = 1000):
        self.functions = built_in_functions.copy()
        self.lambda_funtions = lambda_functions.copy()
        self.variables = {}
        self.includes = {}
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

    def add_function(self, name, fun):
        self.functions[name] = fun

    def get_function(self, name):
        func = self.functions.get(name)
        return func

    def add_variable(self, name, value):
        self.variables[name] = value

    def get_variable(self, name):
        return self.variables.get(name)

    def add_include(self, name, obj):
        self.includes[name] = obj

    def get_include(self, name):
        obj = self.includes.get(name)
        return obj
    
    def increment_recursion_depth(self):
        if self.recursion_depth >= self.recursion_limit:
            raise RecursionLimitExceeded()
        self.recursion_depth += 1

    def decrement_recursion_depth(self):
        if self.recursion_depth > 0:
            self.recursion_depth -= 1

    def new_context(self):
        new_context = Context(self.recursion_limit)
        new_context.functions = self.functions
        new_context.includes = self.includes
        new_context.recursion_depth = self.recursion_depth
        return new_context


class Interpreter:
    def __init__(self, program):
        self.program = program
        self.context = Context()
        self.context.functions.update(program.functions)

    def execute(self, visitor):
        return self.program.accept(visitor, self.context)
