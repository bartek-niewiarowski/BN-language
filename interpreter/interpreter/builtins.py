import numpy as np

class BuiltInFunction:
    def __init__(self, function):
        self.function = function

    def accept(self, visitor, context, args):
        # Wywołaj funkcję z przekazanymi argumentami
        res =  self.function(*args)
        context.last_result = res

class ImportedObject():
    def __init__(self, obj):
        self.obj = obj

    def accept(self, visitor, context, args):
        # Sprawdzamy, czy obiekt jest wywoływalny
        if callable(self.obj):
            # Jeśli obj jest funkcją lub metodą
            context.last_result = self.obj(*args)
        elif hasattr(self.obj, '__call__'):
            # Jeśli obj jest obiektem z metodą __call__ (np. klasa z __call__)
            context.last_result = self.obj.__call__(*args)
        else:
            # Obiekt nie jest funkcją ani metodą; może to być np. instancja klasy lub wartość
            # Możemy zdecydować, co zrobić w takim przypadku, np. zwrócić sam obiekt
            context.last_result = self.obj

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

def where(lst, statements, visitator, context, name):
    result = []
    for item in lst:
        context.add_variable(name, item)
        if statements.accept(visitator, context):
            result.append(item)
    return result

def foreach(lst, statements, visitator, context, name):
    items = []
    for item in lst:
        context.add_variable(name, item)
        #item = statements.accept(visitator, context)
        statements.accept(visitator, context)
        items.append(context.variables.get(name))
    return items

# klasa reprezentująca funkcję wbudowaną
built_in_functions = {
    'print': BuiltInFunction(print),
    'scan': BuiltInFunction(input),
    'to_bool': BuiltInFunction(to_bool),
    'to_int': BuiltInFunction(to_int),
    'to_float': BuiltInFunction(to_float),
    'append': BuiltInFunction(append),
    'remove': BuiltInFunction(remove),
    'sort': BuiltInFunction(sort),
    'get': BuiltInFunction(get),
    'where': BuiltInFunction(where),
    'foreach': BuiltInFunction(foreach)
}

lambda_functions = ['where', 'foreach']
