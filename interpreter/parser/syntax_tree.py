from typing import Union, List
from ..tokens.token_type import TokenType
from ..source.source_position import SourcePosition
from ..tokens.token import Token

class Node:
    def __init__(self, position: SourcePosition) -> None:
        self.position = position

#program = { function_definition }; 
class Program(Node):
    def __init__(self, position, functions) -> None:
        super().__init__(position)
        self.funtions = functions

class FunctionDefintion(Node):
    def __init__(self, position, name, parameters, statements) -> None:
        super().__init__(position)
        self.name = name
        self.parameters = parameters
        self.statements = statements
    
    def __str__(self) -> None:
        return f'Function Declaration: name: {self.name}, parameters: {self.parameters}, statements: {self.statements}'

class IncludeStatement(Node):
    def __init__(self, position: SourcePosition, library_name, objects_names) -> None:
        super().__init__(position)
        self.library_name = library_name
        self.objects_names = objects_names

class LambdaExpression(Node):
    def __init__(self, position: SourcePosition, variable_name, statements) -> None:
        super().__init__(position)
        self.variable_name = variable_name
        self.statements = statements

class FunctionArguments(Node):
    def __init__(self, position: SourcePosition, arguments) -> None:
        super().__init__(position)
        self.arguments = arguments

class Identifier(Node):
    def __init__(self, position, name) -> None:
        super().__init__(position)
        self.name = name
    
    def __str__(self) -> str:
        return f'Identifier: name: {self.name}'

class Arguments(Node):
    def __init__(self, position, args) -> None:
        super().__init__(position)
        self._arguments = args

class Parameter(Node):
    def __init__(self, position, name) -> None:
        super().__init__(position)
        self.name = name

class ReturnStatement(Node):
    def __init__(self,position, statement):
        super().__init__(position)
        self.statement = statement
        
    def __str__(self):
        return f'ReturnStatement({self.statement})'

class IfStatement(Node):
    def __init__(self, position, condition, statements, else_statement) -> None:
        super().__init__(position)
        self.condition = condition
        self.statements = statements
        self.else_statement = else_statement

    def __str__(self):
        return f'IfStatement({self.condition}, {self.statements}, Else({self.else_statement}))'

class WhileStatement(Node):
    def __init__(self, position, condition, statements) -> None:
        super().__init__(position)
        self.condition = condition
        self.statements = statements
    
    def __str__(self):
        return f'WhileStatement({self.condition}, {self.statements})'

class BreakStatement(Node):
    def __init__(self, position) -> None:
        super().__init__(position)

class MultiParameterExpression(Node):
    def __init__(self, position, nodes):
        super().__init__(position)
        self.nodes = nodes
        
    def __str__(self):
        r = ', '.join([str(node) for node in self.nodes])
        return f'{self.__class__.__name__}({r})'

class OrExpression(MultiParameterExpression):
    def __init__(self, position, nodes):
        super().__init__(position, nodes)
        
class AndExpression(MultiParameterExpression):
    def __init__(self, position, nodes):
        super().__init__(position, nodes)

class Negation(Node):
    def __init__(self, position, node):
        super().__init__(position)
        self.node = node
        
    def __str__(self):
        return f'Negation({self.node})'

class ArthExpression(MultiParameterExpression):
    def __init__(self, position, nodes):
        super().__init__(position, nodes)
    
class Term(MultiParameterExpression):
    def __init__(self, position, nodes):
        super().__init__(position, nodes)

class Reciprocal(Node):
    def __init__(self, position, node):
        super().__init__(position)
        self.node = node
        
    def __str__(self):
        return f'Reciprocal({self.node})'

class BinaryOperation(Node):
    def __init__(self, position, left, right):
        super().__init__(position)
        self.left = left
        self.right = right
        
    def __str__(self):
        return f'{self.__class__.__name__}({self.left}, {self.right})'

class EqualOperation(BinaryOperation):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)

class NotEqualOperation(BinaryOperation):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)
        
class GreaterOperation(BinaryOperation):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)
        
class GreaterEqualOperation(BinaryOperation):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)
        
class LessOperation(BinaryOperation):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)
        
class LessEqualOperation(BinaryOperation):
    def __init__(self, position, left, right):
        super().__init__(position, left, right)

class LiteralTrue(Node):
    def __init__(self, position: SourcePosition) -> None:
        super().__init__(position)

class LiteralFalse(Node):
    def __init__(self, position: SourcePosition) -> None:
        super().__init__(position)

class LiteralInt(Node):
    def __init__(self, position: SourcePosition, value) -> None:
        super().__init__(position)
        self.value = value

class LiteralFloat(Node):
    def __init__(self, position: SourcePosition, value) -> None:
        super().__init__(position)
        self.value = value

class LiteralString(Node):
    def __init__(self, position: SourcePosition, value) -> None:
        super().__init__(position)
        self.value = value

class Array(Node):
    def __init__(self, position: SourcePosition, items) -> None:
        super().__init__(position)
        self.items = items

class VariableAssignment(Node):
    def __init__(self, position: SourcePosition, target, value):
        super().__init__(position)
        self.target = target
        self.value = value

    def __str__(self):
        return f'VariableAssignment(target={self.target}, value={self.value})'

class VariableName(Node):
    def __init__(self, position: SourcePosition, id) -> None:
        super().__init__(position)
        self.id = id

class TypicalFunctionCall(Node):
    def __init__(self, position: SourcePosition, function_name, arguments) -> None:
        super().__init__(position)
        self.function_name = function_name
        self.arguments = arguments
    
    def __str__(self):
        return f"TypicalFunctionCall(name:{self.function_name} arguments{self.arguments})"

class ObjectExpression(Node):
    def __init__(self, position: SourcePosition, chained_access: List[Union[VariableName, TypicalFunctionCall]], final_variable: VariableName):
        super().__init__(position)
        self.chained_access = chained_access
        self.final_variable = final_variable

    def __str__(self):
        return f"ObjectExpression({self.chained_access} -> {self.final_variable})"

class FunctionCall(Node):
    def __init__(self, position: SourcePosition, chained_call: List[Union[VariableName, TypicalFunctionCall]], last_call: TypicalFunctionCall) -> None:
        super().__init__(position)
        self.chained_call = chained_call
        self.last_call = last_call

LOGIC_OPERATIONS_MAPPING = {
    TokenType.EQUAL_OPERATOR:                    EqualOperation,
    TokenType.NOT_EQUAL_OPERATOR:                NotEqualOperation,
    TokenType.GREATER_THAN_OPERATOR:             GreaterOperation,
    TokenType.GREATER_OR_EQUAL_THAN_OPERATOR:    GreaterEqualOperation,
    TokenType.LESS_THAN_OPERATOR:                LessOperation,
    TokenType.LESS_OR_EQUAL_THAN_OPERATOR:       LessEqualOperation,
    }
