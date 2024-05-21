import numpy as np

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

built_in_functions = {
    'print': print,
    'scan': input,
    'to_bool': to_bool,
    'to_int': to_int,
    'to_float': to_float,
    'append': append,
    'remove': remove,
    'sort': sort,
    'get': get,
    'where': where,
    'foreach': foreach
}

lambda_functions = ['where', 'foreach']
