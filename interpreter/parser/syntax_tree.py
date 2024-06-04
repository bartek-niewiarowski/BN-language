from ..source.source_position import SourcePosition
from ..interpreter.visitor import Visitor
from abc import abstractmethod
import importlib


class Node:
    def __init__(self, position: SourcePosition) -> None:
        self.position = position

    @abstractmethod
    def accept(self, visitor: Visitor) -> None:
        pass


class Program(Node):
    def __init__(self, position, functions, includes) -> None:
        super().__init__(position)
        self.functions = functions
        self.includes = includes

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_program(self)

    def __str__(self):
        function_definitions = '\n'.join(str(self.functions[function]) for function in self.functions)
        return f"Program at {self.position} with functions:\n{function_definitions}"


class FunctionDefintion(Node):
    def __init__(self, position, name, parameters, statements) -> None:
        super().__init__(position)
        self.name = name
        self.parameters = parameters
        self.statements = statements

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_function_definition(self)

    def __str__(self):
        parameters_str = ", ".join(str(param) for param in self.parameters)
        statements_str = "\n    ".join(str(stmt) for stmt in self.statements)
        return f'Function "{self.name}":\n  Parameters: {parameters_str}\n  Statements:\n    {statements_str}'


class IncludeStatement(Node):
    def __init__(self, position: SourcePosition, library_name, objects_names) -> None:
        super().__init__(position)
        self.library_name = library_name
        self.objects_names = objects_names

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_include_statement(self)

    def __str__(self):
        objects_names = ", ".join(str(object.name) for object in self.objects_names)
        return f'Include {self.library_name} with objects {objects_names}'


class LambdaExpression(Node):
    def __init__(self, position: SourcePosition, variable_name, statements) -> None:
        super().__init__(position)
        self.variable_name = variable_name
        self.statements = statements

    def accept(self, visitor: Visitor):
        visitor.visit_lambda_expression(self)


class FunctionArguments(Node):
    def __init__(self, position: SourcePosition, arguments) -> None:
        super().__init__(position)
        self.arguments = arguments
    
    def accept(self, visitor: Visitor):
        visitor.visit_function_arguments(self)


class Identifier(Node):
    def __init__(self, position, name, parent=None) -> None:
        super().__init__(position)
        self.name = name
        self.parent = parent

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_identifier(self)

    def __str__(self):
        return f'Identifier "{self.name}"'


class Parameter(Node):
    def __init__(self, position, name) -> None:
        super().__init__(position)
        self.name = name

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_parameter(self)

    def __str__(self):
        return f'Parameter "{self.name}"'


class ReturnStatement(Node):
    def __init__(self, position, statement):
        super().__init__(position)
        self.statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_return_statement(self)

    def __str__(self):
        return f'ReturnStatement: {str(self.statement)}'


class IfStatement(Node):
    def __init__(self, position, condition, statements, else_statement) -> None:
        super().__init__(position)
        self.condition = condition
        self.statements = statements
        self.else_statement = else_statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_if_statement(self)

    def __str__(self):
        if_statements_str = "\n     ".join(str(stmt) for stmt in self.statements)
        else_statement_str = "\n    ".join(str(stmt) for stmt in self.else_statement)
        return f'If {self.condition}:\n  Then:\n    {if_statements_str}\n  Else:\n    {else_statement_str}'


class WhileStatement(Node):
    def __init__(self, position, condition, statements) -> None:
        super().__init__(position)
        self.condition = condition
        self.statements = statements

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_while_statement(self)

    def __str__(self):
        stmts_str = "\n".join(str(stmt) for stmt in self.statements)
        return f'While {self.condition} do:\n    {stmts_str}'


class BreakStatement(Node):
    def __str__(self):
        return f'BreakStatement at {self.position}'

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_break_statement(self)


class MultiParameterExpression(Node):
    def __init__(self, position, nodes):
        super().__init__(position)
        self.nodes = nodes

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError("Must be implemented by subclasses")

    def __str__(self):
        nodes_str = ', '.join(str(node) for node in self.nodes)
        return f'{self.__class__.__name__}({nodes_str})'


class OrExpression(MultiParameterExpression):
    def __init__(self, position, nodes):
        super().__init__(position, nodes)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_or_expression(self)

    def __str__(self):
        return super().__str__()


class AndExpression(MultiParameterExpression):
    def __init__(self, position, nodes):
        super().__init__(position, nodes)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_and_expression(self)

    def __str__(self):
        return super().__str__()


class Negation(Node):
    def __init__(self, position, node, negation_type):
        super().__init__(position)
        self.node = node
        self.negation_type = negation_type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_negation(self)

    def __str__(self):
        return f'Negation of ({self.node}) at {self.position}'


class ArthExpression(Node):
    def __init__(self, position, left, right):
        super().__init__(position)
        self.left = left
        self.right = right

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError("Must be implemented by subclasses")

    def __str__(self):
        return f'{self.left} {self.__class__.__name__} {self.right}'


class SumExpression(ArthExpression):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_sum_expression(self)


class SubExpression(ArthExpression):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_sub_expression(self)


class MulExpression(ArthExpression):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_mul_expression(self)


class DivExpression(ArthExpression):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_div_expression(self)


class BinaryOperation(Node):
    def __init__(self, position, left, right):
        super().__init__(position)
        self.left = left
        self.right = right

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError("Must be implemented by subclasses")

    def __str__(self):
        return f'{str(self.left)} {self.__class__.__name__} {str(self.right)}'


class EqualOperation(BinaryOperation):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_equal_operation(self)

    def __str__(self):
        return super().__str__()


class NotEqualOperation(BinaryOperation):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_not_equal_operation(self)

    def __str__(self):
        return super().__str__()


class GreaterOperation(BinaryOperation):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_greater_operation(self)

    def __str__(self):
        return super().__str__()


class GreaterEqualOperation(BinaryOperation):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_greater_equal_operation(self)

    def __str__(self):
        return super().__str__()


class LessOperation(BinaryOperation):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_less_operation(self)

    def __str__(self):
        return super().__str__()


class LessEqualOperation(BinaryOperation):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_less_equal_operation(self)

    def __str__(self):
        return super().__str__()


class LiteralBool(Node):
    def __init__(self, position: SourcePosition, value) -> None:
        super().__init__(position)
        self.value = value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_literal_bool(self)

    def __str__(self):
        return f'{self.value} at {self.position}'


class LiteralInt(Node):
    def __init__(self, position: SourcePosition, value) -> None:
        super().__init__(position)
        self.value = value

    def accept(self, visitor: Visitor):
        visitor.visit_literal_int(self)

    def __str__(self):
        return f'Integer value {self.value}'


class LiteralFloat(Node):
    def __init__(self, position: SourcePosition, value) -> None:
        super().__init__(position)
        self.value = value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_literal_float(self)

    def __str__(self):
        return f'Float value {self.value}'


class LiteralString(Node):
    def __init__(self, position: SourcePosition, value) -> None:
        super().__init__(position)
        self.value = value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_literal_string(self)

    def __str__(self):
        return f'String value "{self.value}"'


class Array(Node):
    def __init__(self, position: SourcePosition, items) -> None:
        super().__init__(position)
        self.items = items

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_array(self)

    def __str__(self):
        items_str = ', '.join(str(item) for item in self.items)
        return f'Array [{items_str}]'


class Assignment(Node):
    def __init__(self, position: SourcePosition, target, value):
        super().__init__(position)
        self.target = target
        self.value = value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_assignment(self)

    def __str__(self):
        return f'VariableAssignment of {str(self.target)} to {str(self.value)}'


class FunctionCall(Node):
    def __init__(self, position: SourcePosition, function_name, arguments, parent=None) -> None:
        super().__init__(position)
        self.function_name = function_name
        self.arguments = arguments
        self.parent = parent

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_function_call(self)

    def __str__(self):
        return f'TypicalFunctionCall to {self.function_name} with arguments ({str(self.arguments)})'


class Statements(Node):
    def __init__(self, position: SourcePosition, statements) -> None:
        super().__init__(position)
        self.statements = statements
    
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_statements(self)
