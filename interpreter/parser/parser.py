from typing import Optional
from ..tokens.token import Token 
from ..tokens.token import TokenType
from ..lexer.lexer import Lexer
from .syntax_error import *
from .syntax_tree import *
import sys

class Parser:
    def  __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.current_token = None
        self.consume_token()

        self.LOGIC_OPERATORS = {
        TokenType.EQUAL_OPERATOR,
        TokenType.NOT_EQUAL_OPERATOR,
        TokenType.GREATER_THAN_OPERATOR,
        TokenType.GREATER_OR_EQUAL_THAN_OPERATOR,
        TokenType.LESS_THAN_OPERATOR,
        TokenType.LESS_OR_EQUAL_THAN_OPERATOR
        }

        self.ARTH_OPERATORS = {
            TokenType.ADD_OPERATOR,
            TokenType.SUB_OPERATOR
        }

        self.TERM_OPERATORS = {
            TokenType.MUL_OPERATOR,
            TokenType.DIV_OPERATOR
        }

        self.BOOLEAN = {
            TokenType.TRUE_VALUE,
            TokenType.FALSE_VALUE
        }
    
    def raise_exception(self, token_type):
        raise ExpectedExpressionError(self.current_token, token_type)

    def consume_token(self):
        self.current_token = self.lexer.get_next_token()
    
    def check_token_type(self, types) -> bool:
        if isinstance(types, TokenType):
            types = {types}
        return self.current_token.type in types

    def try_consume(self, types):
        if not self.check_token_type(types):
           return None
        token = self.current_token
        self.consume_token()
        return token
    
    def must_be(self, types):
        if not self.check_token_type(types):
           self.raise_exception(types)
        token = self.current_token
        self.consume_token()
        return token
    
    def check_parsed(self, expr, type):
        if expr is None:
            if isinstance(type, TokenType):
                self.raise_exception(type)
            else:
                raise SyntaxError
        return expr

    # program = { function_definition }; 
    def parse_program(self):
        functions = {}
        position = self.current_token.position
        while funDef := self.parse_function_definition():
            if name := funDef.name in functions:
                RedefintionFuntionError(self.current_token, name)
            else:
                functions[name] = funDef
        return Program(position, functions)
    
    # function_definition = "def", function_name, "(", parameters , ")" , statements; 
    def parse_function_definition(self) -> Optional[FunctionDefintion]:
        if not self.try_consume(TokenType.DEF):
            return None
        position = self.current_token.position
        name = self.must_be(TokenType.ID).value
        self.must_be(TokenType.LEFT_BRACKET)
        params = self.parse_parameters()
        self.must_be(TokenType.RIGHT_BRACKET)
        statements = self.parse_statements()
        if statements is None:
            EmptyBlockOfStatements(self.current_token)
        return FunctionDefintion(position, name, params, statements)

    # include_statement = "from", library_name, "import", object_name, 	{coma, object_name}, semicolon; 
    def parse_include_statement(self):
        if not self.try_consume(TokenType.FROM_NAME):
            return None
        position = self.current_token.position
        library_name = self.must_be(TokenType.ID)
        self.must_be(TokenType.IMPORT_NAME)
        object_names = []
        object_name = self.must_be(TokenType.ID)
        object_names.append(object_name)
        while self.try_consume(TokenType.COMMA):
            object_name = self.must_be(TokenType.ID)
            object_names.append(object_name)
        self.must_be(TokenType.SEMICOLON)
        return IncludeStatement(position, library_name, object_names)
    
    # lambda_expression = "$", variable_name, "=>", statements; 
    def parse_lambda_expression(self):
        if not self.try_consume(TokenType.LAMBDA_ID):
            return None
        position = self.current_token.position
        variable_name = self.must_be(TokenType.ID)

        self.must_be(TokenType.LAMBDA_OPERATOR)
        statements = self.parse_statements()
        return LambdaExpression(position, variable_name, statements)
    
    # function_call = chained_expression, typical_function_call, semicolon;
    def parse_function_call_or_variable_assignment(self):
        if chained_expression := self.parse_chained_expression():
            if isinstance(chained_expression[-1], TypicalFunctionCall):
                return FunctionCall(chained_expression[0].position, chained_expression[0:-1], chained_expression[-1])
            return self.parse_variable_assignment(chained_expression)
        return None
    
    # chained_expression = {variable_name | typical_function_call, dot}; 
    def parse_chained_expression(self):
        chain = []
        if not (element := self.parse_id()):
            return None
        chain.append(element)
        while self.try_consume(TokenType.DOT):
            if not (element := self.parse_id()):
                raise SyntaxError("There is no variable access or function call after DOT.")
            chain.append(element)
        return chain

    def parse_id(self):
        if not (token := self.try_consume(TokenType.ID)):
            return None
        if element := self.parse_typical_function_call(token):
            return element
        else:
            return VariableName(token.position, token.value)
    
    def parse_typical_function_call(self, token: Token):
        if not self.try_consume(TokenType.LEFT_BRACKET):
            return None
        arguments = self.parse_arguments()
        self.must_be(TokenType.RIGHT_BRACKET)
        return TypicalFunctionCall(token.position, token.value, arguments)
        
    # parameters = [ variable_name, {comma, variable_name} ]; 
    def parse_parameters(self):
        params = []
        if (param := self.parse_parameter()) == None:
            return params
        params.append(param)
        while self.try_consume(TokenType.COMMA):
            param = self.parse_parameter()
            if param == None:
                InvalidParametersDefintion(self.current_token)
            elif param in params:
                TwoParametersWithTheSameName(self.current_token, param) #ale rzucimy zla pozycje, o jeden token za daleko
            else:
                params.append(param)
        return params

    def parse_parameter(self):
        position = self.current_token.position
        if param := self.try_consume(TokenType.ID).value:
            return Parameter(position, param)
        return None
    
    # statements = "{", {statement}, "}"; 
    def parse_statements(self):
        self.must_be(TokenType.LEFT_CURLY_BRACKET)
        statements = []
        while stm := self.parse_statement():
            statements.append(stm)
        self.must_be(TokenType.RIGHT_CURLY_BRACKET)
        return statements
        
    def parse_statement(self):
        stm = \
            self.parse_return_statement() \
            or self.parse_if_statement() \
            or self.parse_break_statement() \
            or self.parse_while_statement() \
            or self.parse_function_call_or_variable_assignment()

        if stm:
            return stm
        return None

    def parse_return_statement(self):
        position = self.current_token.position
        if not self.try_consume(TokenType.RETURN_NAME):
            return None
        self.must_be(TokenType.LEFT_BRACKET)
        expr = self.parse_or_expression()
        self.must_be(TokenType.RIGHT_BRACKET)
        self.must_be(TokenType.SEMICOLON)
        return ReturnStatement(position, expr)

    #if = "if", "(", expression, ")", statements, ["else", statements]; 
    def parse_if_statement(self):
        if not self.try_consume(TokenType.IF_NAME):
            return None
        self.must_be(TokenType.LEFT_BRACKET)
        if_condition = self.parse_or_expression()
        self.must_be(TokenType.RIGHT_BRACKET)
        if_statements = self.parse_statements()
        else_statements = None
        if self.try_consume(TokenType.ELSE_NAME):
            else_statements = self.parse_statements()
        return IfStatement(if_condition, if_statements, else_statements)

    #while = "while", "(", expression, ")", statements; 
    def parse_while_statement(self):
        if self.try_consume(TokenType.WHILE_NAME):
            self.must_be(TokenType.LEFT_BRACKET)
            while_condition = self.parse_or_expression()
            self.must_be(TokenType.RIGHT_BRACKET)
            while_statements = self.parse_statements()
            return WhileStatement(while_condition, while_statements)
        return None
    
    # break_statement = "break", semicolon ; 
    def parse_break_statement(self):
        position = self.current_token.position
        if not self.try_consume(TokenType.BREAK_NAME):
            return None
        self.must_be(TokenType.SEMICOLON)
        return BreakStatement(position)

    # or_expression = and_expression, {"or", and_expression}; 
    def parse_or_expression(self):
        position = self.current_token.position
        if left := self.parse_and_expression():
            expressions = [left]
            while self.try_consume(TokenType.OR_OPERATOR):
                if expression := self.parse_and_expression():
                    expressions.append(expression)
            if len(expressions) == 1:
                return left
            return OrExpression(position, expressions)
        else:
            return None

    # and_expresion = relation_expresion, {"and", relation_condition}; 
    def parse_and_expression(self):
        position = self.current_token.position
        if left := self.parse_logic_expression():
            expressions = [left]
            while self.try_consume(TokenType.AND_OPERATOR):
                if expression := self.parse_logic_expression:
                    expressions.append(expression)
            if len(expressions) == 1:
                return left
            return OrExpression(position, expressions)
        else:
            return None

    # logic_expression = arth_expression, [relational_operator, arth_expression]; 
    def parse_logic_expression(self):
        position = self.current_token.position
        if left := self.parse_arth_expression():
            if token := self.try_consume(self.LOGIC_OPERATORS):
                right = self.parse_arth_expression()
                return LOGIC_OPERATIONS_MAPPING.get(token.type)(position, left, right)
            return left        
    
    # arth_expression = term, {sum_operator, term}; 
    def parse_arth_expression(self):
        position = self.current_token.position
        if left := self.parse_term():
            expressions = [left]
            while (token := self.try_consume(self.ARTH_OPERATORS)):
                next_expr = self.parse_term()
                if token.type == TokenType.SUB_OPERATOR:
                    next_expr = Negation(token.type, next_expr)
                expressions.append(next_expr)
                    
            if len(expressions) == 1:
                return left
            else:
                return ArthExpression(position, expressions)
    
    # term = factor, { multiply_operator, factor }; 
    def parse_term(self):
        position = self.current_token.position
        if left := self.parse_factor():
            expressions = [left]
            while (token := self.try_consume(self.TERM_OPERATORS)):
                next_expr = self.parse_factor()
                if token.type == TokenType.DIV_OPERATOR:
                    next_expr = Reciprocal(next_expr.position, next_expr)
                expressions.append(next_expr)
                    
            if len(expressions) == 1:
                return left
            else:
                return Term(position, expressions)
    
    # factor = {negation_operator}, variable_value | "(", arth_expression, ")"; 
    def parse_factor(self):
        position = self.current_token.position
        negation_counter = 0
        while self.try_consume([TokenType.NEGATION_OPERATOR, TokenType.SUB_OPERATOR]):
            negation_counter += 1
        factor = \
            self.parse_variable_value() \
            or self.parse_expression()
        if factor:
            for _ in range(negation_counter):
                factor = Negation(position, factor)
            return factor
        raise InvalidStatement(self.current_token, 'abc')

    #variable_value = bool_value | int_value | float_value| string_value | array | variable_name;
    def parse_variable_value(self):
        variable_value = \
            self.parse_boolean()    \
            or self.parse_number()  \
            or self.parse_float()   \
            or self.parse_string()  \
            or self.parse_array()   \
            or self.parse_variable_name()
        if variable_value:
            return variable_value
        return None

    def parse_expression(self):
        if self.try_consume(TokenType.LEFT_BRACKET):
            operation = self.parse_arth_expression()
            self.must_be(TokenType.RIGHT_BRACKET)
            return operation
        return None
    
    def parse_boolean(self):
        position = self.current_token.position
        if token := self.try_consume(self.BOOLEAN):
            if token.type == TokenType.TRUE_VALUE:
                return LiteralTrue(position)
            return LiteralFalse(position)
        return None

    def parse_number(self):
        position = self.current_token.position
        if token := self.try_consume(TokenType.INT_VALUE):
            return LiteralInt(position, token.value)
        return None

    def parse_float(self):
        position = self.current_token.position
        if token := self.try_consume(TokenType.FLOAT_VALUE):
            return LiteralFloat(position, token.value)
        return None

    def parse_string(self):
        position = self.current_token.position
        if token := self.try_consume(TokenType.STRING_VALUE):
            return LiteralString(position, token.value)
        return None

    # array= "[", [or_expression, {comma , or_expression}] , "]"; 
    def parse_array(self):
        if not self.try_consume(TokenType.LEFT_QUADRATIC_BRACKET):
            return None
        position = self.current_token.position
        elements = []

        if self.try_consume(TokenType.RIGHT_QUADRATIC_BRACKET):
            return Array(position, elements)

        first_element = self.parse_or_expression()
        if first_element is None:
            raise SyntaxError("Expected an expression as an array element at position {}".format(position))
        elements.append(first_element)

        while self.try_consume(TokenType.COMMA):
            next_element = self.parse_or_expression()
            if next_element is None:
                raise SyntaxError("Expected an expression after ',' in array at position {}".format(position))
            elements.append(next_element)

        if not self.try_consume(TokenType.RIGHT_QUADRATIC_BRACKET):
            raise SyntaxError("Expected ']' at the end of array at position {}".format(position))
        
        return Array(position, elements)
    
    # variable_name = identifier;
    def parse_variable_name(self):
        position = self.current_token.position
        if token := self.try_consume(TokenType.ID):
            return Identifier(position, token.value)
        return None
    
    # arguments = [ expression, {comma, expression} ] | lambda_expression; 
    def parse_arguments(self):
        arguments = \
        self.parse_lambda_expression() \
        or self.parse_function_arguments()

        return arguments
    
    def parse_function_arguments(self):
        position = self.current_token.position
        arguments = []
        while arg := self.parse_or_expression():
            arguments.append(arg)     
        
        return FunctionArguments(position, arguments)
    
    # variable_assignment = object_expression, assign_operator, assign_expression, semicolon; 
    def parse_variable_assignment(self, chained_expression):
        if not isinstance(chained_expression[-1], VariableName):
            raise SyntaxError()
        object_expression = ObjectExpression(chained_expression[0].position, chained_expression[0:-1], chained_expression[-1])
        self.must_be(TokenType.ASSIGN_OPERATOR)
        if not (assign_expr := self.parse_assign_expression()):
            raise SyntaxError()
        return VariableAssignment(chained_expression[0].position, object_expression, assign_expr)
    
    # assign_expression = or_expression | object_expression | function_call
    def parse_assign_expression(self):
        if asign_expression := self.parse_or_expression():
            return asign_expression
        if chained_expression := self.parse_chained_expression():
            if isinstance(chained_expression[-1], VariableName):
                return ObjectExpression(chained_expression[0].position, chained_expression[0:-1], chained_expression[-1])
            elif isinstance(chained_expression[-1], TypicalFunctionCall):
                return TypicalFunctionCall(chained_expression[0].position, chained_expression[0:-1], chained_expression[-1])
            else:
                raise SyntaxError()
        return None