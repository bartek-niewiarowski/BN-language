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

built_in_functions = {'print': print,
                      'scan': input,
                      'to_bool': to_bool,
                      'to_int': to_int,
                      'to_float': to_float,
                      }
