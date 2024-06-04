import numpy as np

class BuiltInFunction:
    def __init__(self, function):
        self.function = function

    def accept(self, visitor):
        visitor.visit_built_in_function(self)

class LambdaFunction(BuiltInFunction):
    def __init__(self, function):
        super().__init__(function)
    
    def accept(self, visitor):
        visitor.visit_lambda_function(self)

class ImportedObject():
    def __init__(self, obj):
        self.obj = obj

    def accept(self, visitor):
        visitor.visit_imported_object(self)

def to_bool(x):
    if isinstance(x, np.ndarray):
        return x.astype(bool)
    return bool(x)

def to_int(x):
    if isinstance(x, np.ndarray):
        return x.astype(int)
    return int(x)

def to_float(x):
    if isinstance(x, np.ndarray):
        return x.astype(float)
    return float(x)

def append(lst, value):
    lst.append(value)

def remove(lst, index):
    if 0 <= index < len(lst):
        lst.pop(index)
    else:
        raise IndexError("Index out of range")

def sort(lst):
    if all(isinstance(i, (int, float)) for i in lst):
        lst.sort()
    else:
        raise ValueError("List contains non-numeric elements")

def get(lst, index):
    if 0 <= index < len(lst):
        return lst[index]
    else:
        raise IndexError("Index out of range")

def where(visitor, lst, name, statements):
    result = []
    for item in lst:
        visitor.context.add_variable(name, item)
        statements.accept(visitor)
        if visitor.last_result:
            result.append(item)
    return result

def foreach(visitor, lst, name, statements):
    items = []
    for item in lst:
        visitor.context.add_variable(name, item)
        statements.accept(visitor)
        items.append(visitor.context.variables.get(name))
    return items

def scan(prompt):
    print(prompt)
    val = input()
    return val

# klasa reprezentująca funkcję wbudowaną
built_in_functions = {
    'print': BuiltInFunction(print),
    'scan': BuiltInFunction(scan),
    'to_bool': BuiltInFunction(to_bool),
    'to_int': BuiltInFunction(to_int),
    'to_float': BuiltInFunction(to_float),
    'append': BuiltInFunction(append),
    'remove': BuiltInFunction(remove),
    'sort': BuiltInFunction(sort),
    'get': BuiltInFunction(get),
    'where': LambdaFunction(where),
    'foreach': LambdaFunction(foreach)
}
