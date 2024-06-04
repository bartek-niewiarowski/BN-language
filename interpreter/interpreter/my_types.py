class ObjectValue:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Int(ObjectValue):
    def __add__(self, other):
        if isinstance(other, Int):
            return Int(self.value + other.value)
        elif isinstance(other, Float):
            return Float(self.value + other.value)
        elif isinstance(other, String):
            return String(str(self.value) + other.value)
        else:
            return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, Int):
            return Int(self.value - other.value)
        elif isinstance(other, Float):
            return Float(self.value - other.value)
        else:
            return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, Int):
            return Int(self.value * other.value)
        elif isinstance(other, String):
            return String(other.value * self.value)
        elif isinstance(other, Float):
            return Float(self.value * other.value)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, Int):
            if other.value == 0:
                raise ZeroDivisionError("Division by zero is not allowed")
            return Int(self.value // other.value)
        elif isinstance(other, Float):
            if other.value == 0.0:
                raise ZeroDivisionError("Division by zero is not allowed")
            return Float(self.value / other.value)
        else:
            return NotImplemented
    
    def __neg__(self):
        return Float(-self.value)

class String(ObjectValue):
    def __add__(self, other):
        if isinstance(other, (String, Int, Float)):
            return String(self.value + str(other.value))
        else:
            return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, Int):
            return String(self.value * other.value)
        elif isinstance(other, String):
            return String(self.value * other.value)  # self.value będzie 1 dla True i 0 dla False
        else:
            return NotImplemented

class Float(ObjectValue):
    def __add__(self, other):
        if isinstance(other, (Int, Float)):
            return Float(self.value + float(other.value))
        elif isinstance(other, String):
            return String(str(self.value) + other.value)
        else:
            return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, (Int, Float)):
            return Float(self.value - float(other.value))
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (Int, Float)):
            return Float(self.value * float(other.value))
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (Int, Float)):
            if float(other.value) == 0.0:
                raise ZeroDivisionError("Division by zero is not allowed")
            return Float(self.value / float(other.value))
        else:
            return NotImplemented
    
    def __neg__(self):
        return Float(-self.value)

class Array(ObjectValue):
    def __add__(self, other):
        if isinstance(other, Array):
            return Array(self.value + other.value)
        else:
            return NotImplemented
    
    # set_value
    # get_atribute
    # set_atribute
    # call_method

class Bool(ObjectValue):
    def __add__(self, other):
        if isinstance(other, Bool):
            return Bool(self.value or other.value)  # Simplified logic for example
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Bool):
            return Bool(self.value and not other.value)  # Przykład operacji, choć nietypowy dla bool
        else:
            return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, String):
            return String(self.value * other.value)  # self.value będzie 1 dla True i 0 dla False
        else:
            return NotImplemented
    
    def __neg__(self):
        return Bool(not self.value)  # Logiczna negacja True -> False, False -> True