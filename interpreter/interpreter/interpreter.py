from .builtins import built_in_functions


class Context:
    def __init__(self):
        self.functions = built_in_functions.copy()
        self.variables = {}
        self.includes = {}

    def add_function(self, name, fun):
        self.functions[name] = fun

    def get_function(self, name):
        func = self.functions.get(name)
        return func

    def add_variable(self, name, value):
        self.variables[name] = value

    def get_variable(self, name):
        var = self.variables.get(name)
        return var

    def add_include(self, name, obj):
        self.includes[name] = obj

    def get_include(self, name):
        obj = self.includes.get(name)
        return obj

    def new_context(self):
        new_context = Context()
        new_context.functions = self.functions
        return new_context


class Interpreter:
    def __init__(self, program):
        self.program = program
        self.context = Context()

    def execute(self):
        return self.program.accept(self.context)
