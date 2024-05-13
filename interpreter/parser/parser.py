from typing import Optional
from ..tokens.token import Token 
from ..tokens.token import TokenType
from ..lexer.lexer import Lexer
from .syntax_error import *
from .syntax_tree import *

class Parser:
    def  __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.current_token = None
        self.consume_token()

        self.ARTH_OPERATORS = {
            TokenType.ADD_OPERATOR: SumExpression,
            TokenType.SUB_OPERATOR: SubExpression
        }

        self.MUL_OPERATORS = {
            TokenType.MUL_OPERATOR: MulExpression,
            TokenType.DIV_OPERATOR: DivExpression
        }

        self.BOOLEAN = {
            TokenType.TRUE_VALUE,
            TokenType.FALSE_VALUE
        }

        self.LOGIC_OPERATIONS_MAPPING = {
            TokenType.EQUAL_OPERATOR:                    EqualOperation,
            TokenType.NOT_EQUAL_OPERATOR:                NotEqualOperation,
            TokenType.GREATER_THAN_OPERATOR:             GreaterOperation,
            TokenType.GREATER_OR_EQUAL_THAN_OPERATOR:    GreaterEqualOperation,
            TokenType.LESS_THAN_OPERATOR:                LessOperation,
            TokenType.LESS_OR_EQUAL_THAN_OPERATOR:       LessEqualOperation,
            }
    
    def raise_exception(self, token_type):
        raise ExpectedExpressionError(self.current_token, token_type) #currentTokenType na tekst?

    def consume_token(self):
        self.current_token = self.lexer.get_next_token()
        if self.current_token.type == TokenType.COMMENT:
            self.consume_token()
    
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
    
    # program = { include_statement | function_definition };
    # dodanie do funcrions/includes w funkcji parsujacej te konsytrukcje 
    def parse_program(self):
        functions = {}
        includes = []
        position = self.current_token.position

        while self.parse_function_definition(functions) or self.parse_include_statement(includes):
            continue
        if self.current_token.type != TokenType.EOF:
            raise ParsingError(self.current_token, 'Invalid syntax, after parsing a program there is left')
        if not functions and not includes:
            raise ParsingError(self.current_token, 'Invalid syntax, there is no possibility to build program.')

        return Program(position, functions, includes)
    
    # function_definition = "def", function_name, "(", parameters , ")" , statements; 
    def parse_function_definition(self, functions) -> Optional[FunctionDefintion]:
        if not self.try_consume(TokenType.DEF):
            return None
        position = self.current_token.position
        if functions.get(name := self.must_be(TokenType.ID).value):
            raise RedefintionFuntionError(self.current_token, name)
        self.must_be(TokenType.LEFT_BRACKET)
        params = self.parse_parameters()
        self.must_be(TokenType.RIGHT_BRACKET)
        statements = self.parse_statements()
        if not statements:
            ExpectedBlockStatements(self.current_token, 'Expected block statements in function definition')
        functions[name] = (fun := FunctionDefintion(position, name, params, statements))
        return fun

    # include_statement = "from", library_name, "import", object_name, 	{coma, object_name}, semicolon; 
    def parse_include_statement(self, includes):
        if not self.try_consume(TokenType.FROM_NAME):
            return None
        position = self.current_token.position
        library_name = self.must_be(TokenType.ID).value
        self.must_be(TokenType.IMPORT_NAME)
        object_names = []
        object_name = self.must_be(TokenType.ID).value
        object_names.append(object_name)
        while self.try_consume(TokenType.COMMA):
            object_name = self.must_be(TokenType.ID).value
            object_names.append(object_name)
        self.must_be(TokenType.SEMICOLON)
        includes.append(inc := IncludeStatement(position, library_name, object_names))
        return inc
    
    # lambda_expression = "$", variable_name, "=>", statements; 
    def parse_lambda_expression(self):
        if not self.try_consume(TokenType.LAMBDA_ID):
            return None
        position = self.current_token.position
        variable_name = self.must_be(TokenType.ID).value

        self.must_be(TokenType.LAMBDA_OPERATOR)
        if not (statements := self.parse_statements()):
            ExpectedBlockStatements(self.current_token, 'Expected block statements after lambda expression')
        return LambdaExpression(position, variable_name, statements)
    
    # function_call = chained_expression, typical_function_call, semicolon;
    def parse_function_call_or_assignment(self):
        if expression := self.parse_chained_expression():
            if isinstance(expression, FunctionCall):
                self.must_be(TokenType.SEMICOLON)
                return expression
            return self.parse_variable_assignment(expression)
        return None
    
    def parse_function_call_or_object_expression(self):
        if expression := self.parse_chained_expression():
            if isinstance(expression, FunctionCall) or isinstance(expression, Identifier):
                return expression
        return None
    
    # chained_expression = variable_name, ["(", arguments, ")"]{dot, (variable_name | typical_function_call)}; 
    def parse_chained_expression(self):
        if not (element := self.parse_id(None)):
            return None
        while self.try_consume(TokenType.DOT):
            if not (element := self.parse_id(element)):
                raise ParsingError(self.current_token, "There is no variable access or function call after DOT.")
        return element

    def parse_id(self, parent):
        if not (token := self.try_consume(TokenType.ID)):
            return None
        if element := self.parse_typical_function_call(token, parent):
            return element
        else:
            return Identifier(token.position, token.value, parent) #parent
    
    def parse_typical_function_call(self, token: Token, parent):
        if not self.try_consume(TokenType.LEFT_BRACKET):
            return None
        arguments = self.parse_arguments()
        self.must_be(TokenType.RIGHT_BRACKET)
        return FunctionCall(token.position, token.value, arguments, parent) #parent
    # drzewo dla FunctionCall i Identifier, ktore maja parenta
        
    # parameters = [ variable_name, {comma, variable_name} ]; 
    def parse_parameters(self):
        params = []
        if (param := self.parse_parameter()) == None:
            return params
        params.append(param)
        while self.try_consume(TokenType.COMMA):
            if not (param := self.parse_parameter()):
                raise InvalidParametersDefintion(self.current_token)
            elif param in params:
                raise TwoParametersWithTheSameName(self.current_token, param)
            else:
                params.append(param)
        return params

    # czy warto obudowywac?
    def parse_parameter(self):
        if param := self.try_consume(TokenType.ID):
            return param.value
        return None
    
    # statements = "{", {statement}, "}";
    # obudowanie bloku stms w klase
    # zmiana aby w przyszlosci dopuscic brak bloku statements,  self.must_be(TokenType.LEFT_CURLY_BRACKET) - try_consume
    def parse_statements(self):
        if not self.try_consume(TokenType.LEFT_CURLY_BRACKET): 
            return None
        position = self.current_token.position
        statements = []
        while stm := self.parse_statement():
            statements.append(stm)
        self.must_be(TokenType.RIGHT_CURLY_BRACKET)
        if len(statements) == 0:
            raise EmptyBlockOfStatements(self.current_token)
        return Statements(position, statements)
        
    def parse_statement(self):
        if stm := \
            self.parse_return_statement() \
            or self.parse_if_statement() \
            or self.parse_break_statement() \
            or self.parse_while_statement() \
            or self.parse_function_call_or_assignment():
            return stm
        return None
    
    # nawiasy do wyrzucenia
    def parse_return_statement(self):
        position = self.current_token.position
        if not self.try_consume(TokenType.RETURN_NAME):
            return None
        expr = self.parse_or_expression()
        self.must_be(TokenType.SEMICOLON)
        return ReturnStatement(position, expr)

    #if = "if", "(", expression, ")", statements, ["else", statements]; 
    def parse_if_statement(self):
        if not self.try_consume(TokenType.IF_NAME):
            return None
        position = self.current_token.position
        self.must_be(TokenType.LEFT_BRACKET)
        if not (if_condition := self.parse_or_expression()):
            raise EmptyIfCondition(self.current_token)
        self.must_be(TokenType.RIGHT_BRACKET)
        if not (if_statements := self.parse_statements()):
            ExpectedBlockStatements(self.current_token, 'Expected block statements in if statement')
        else_statements = None
        if self.try_consume(TokenType.ELSE_NAME):
            if not (else_statements := self.parse_statements()):
                raise ExpectedBlockStatements(self.current_token, 'Expected block statements in else statement')
        return IfStatement(position, if_condition, if_statements, else_statements)

    #while = "while", "(", expression, ")", statements; 
    def parse_while_statement(self):
        if self.try_consume(TokenType.WHILE_NAME):
            position = self.current_token.position
            self.must_be(TokenType.LEFT_BRACKET)
            if not (while_condition := self.parse_or_expression()):
                raise InvalidStatement(self.current_token, "Invalid while condition")
            self.must_be(TokenType.RIGHT_BRACKET)
            if not (while_statements := self.parse_statements()):
                ExpectedBlockStatements(self.current_token, 'Expected block statements in while statement')
            return WhileStatement(position, while_condition, while_statements)
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
                else:
                    raise InvalidOrExpression(self.current_token)
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
                if expression := self.parse_logic_expression():
                    expressions.append(expression)
                else:
                    raise InvalidAndExpression(self.current_token)
            if len(expressions) == 1:
                return left
            return AndExpression(position, expressions)
        else:
            return None

    # logic_expression = arth_expression, [relational_operator, arth_expression];
    # skorzystac z jednego LOGIC_OPERATORS,  
    def parse_logic_expression(self):
        position = self.current_token.position
        if left := self.parse_arth_expression():
            if creator := self.LOGIC_OPERATIONS_MAPPING.get(self.current_token.type):
                self.consume_token()
                if right := self.parse_arth_expression():
                    return creator(position, left, right)
                raise InvalidLogicExpression(self.current_token)
        return left       
    
    # arth_expression = term, {sum_operator, term};
    # wyrzucic negacje, AddExpression, SubExpression, kolejna mapa 
    def parse_arth_expression(self):
        if left := self.parse_term():
            while creator := self.ARTH_OPERATORS.get(self.current_token.type):
                self.consume_token()
                if not (next_expr := self.parse_term()):
                    raise InvalidArthExpression(self.current_token)
                left = creator(self.current_token.position, left,  next_expr)
            return left
        return None
    
    # term = factor, { multiply_operator, factor }; 
    def parse_term(self):
        if left := self.parse_factor():
            while creator := self.MUL_OPERATORS.get(self.current_token.type):
                self.consume_token()
                if next_expr := self.parse_factor():
                    left = creator(self.current_token.position, left, next_expr)
                else:
                    raise InvalidTerm(self.current_token)              
            return left
        return None
    
    # factor = [negation_operator], (literal_value | object_expression | function_call | "(", arth_expression, ")");
    # modyfikacja do pijedyncznego znaku negacji  
    def parse_factor(self):
        position = self.current_token.position
        is_negation = False
        if self.try_consume([TokenType.NEGATION_OPERATOR, TokenType.SUB_OPERATOR]):
            is_negation = True
        factor = \
            self.parse_variable_value() \
            or self.parse_function_call_or_object_expression() \
            or self.parse_expression()
        if factor:
            if is_negation:
                factor = Negation(position, factor)
            return factor
        if is_negation and not factor:
            raise InvalidFactor(self.current_token)
        return None
    
    #literal_value = bool_value | int_value | float_value| string_value | array;
    def parse_variable_value(self):
        variable_value = \
            self.parse_boolean()    \
            or self.parse_number()  \
            or self.parse_float()   \
            or self.parse_string()  \
            or self.parse_array()
        if variable_value:
            return variable_value
        return None

    def parse_expression(self):
        if self.try_consume(TokenType.LEFT_BRACKET):
            operation = self.parse_or_expression()
            self.must_be(TokenType.RIGHT_BRACKET)
            return operation
        return None
    
    # LiteralBool i value
    def parse_boolean(self):
        position = self.current_token.position
        if token := self.try_consume(self.BOOLEAN):
            if token.type == TokenType.TRUE_VALUE:
                return LiteralBool(position, True)
            return LiteralBool(position, False)
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

        if first_element := self.parse_or_expression():
            elements.append(first_element)

            while self.try_consume(TokenType.COMMA):
                if (next_element := self.parse_or_expression()) is None:
                    raise InvalidArrayDefinition(self.current_token, "Expected an expression after ',' in array")
                elements.append(next_element)
        
        self.must_be(TokenType.RIGHT_QUADRATIC_BRACKET)
        
        return Array(position, elements)
    
    # arguments = [ expression, {comma, expression} ] | lambda_expression; 
    def parse_arguments(self):
        arguments = \
        self.parse_lambda_expression() \
        or self.parse_function_arguments()
        return arguments
    
    def parse_function_arguments(self):
        position = self.current_token.position
        arguments = []
        if arg := self.parse_or_expression():
            arguments.append(arg)
            while self.try_consume(TokenType.COMMA):
                arguments.append(self.parse_or_expression())
        
        return FunctionArguments(position, arguments)
    
    # variable_assignment = object_expression, assign_operator, assign_expression, semicolon; 
    def parse_variable_assignment(self, expression):
        if not isinstance(expression, Identifier):
            raise InvalidVariableAssignment(self.current_token, 'You define invalid variable assignment')
        self.must_be(TokenType.ASSIGN_OPERATOR)
        if not (assign_expr := self.parse_or_expression()):
            raise InvalidVariableAssignment(self.current_token, 'You define invalid variable assignment')
        self.must_be(TokenType.SEMICOLON)
        return Assignment(expression.position, expression, assign_expr) #Assignment
