from ..tokens.token import Token

class ParsingError(Exception):
    def __init__(self, token, message=''):
        message = f"SyntaxError at position: line: {token.position.line}, col: {token.position.column}.\n{message}"
        super().__init__(message)
    
class ExpectedExpressionError(ParsingError):
    def __init__(self, token, expected_tokens):
        if not isinstance(expected_tokens, list):
            expected_tokens = [expected_tokens]
        expected_types = ', '.join(expected_token.name for expected_token in expected_tokens)
        message = f'Expected token of type(s) {expected_types} but got type {token.type.name}'
        super().__init__(token, message)

class RedefintionFuntionError(ParsingError):
    def __init__(self, token, name):
        message = f'You are trying to redefine function: {name}'
        super().__init__(token, message)

class EmptyBlockOfStatements(ParsingError):
    def __init__(self, token):
        message = f'You define function with empty block of statements.'
        super().__init__(token, message)

class InvalidParametersDefintion(ParsingError):
    def __init__(self, token):
        message = f'Invalid parameters definiton, there is no parameter after comma.'
        super().__init__(token, message)

class TwoParametersWithTheSameName(ParsingError):
    def __init__(self, token, name):
        message = f'You are trying to define function with two same parameters: {name}'
        super().__init__(token, message)

class InvalidStatement(ParsingError):
    def __init__(self, token, name):
        message = f'You define invalid statement.'
        super().__init__(token, message)

class InvalidFactor(ParsingError):
    def __init__(self, token, name):
        message = f'You define invalid factor.'
        super().__init__(token, message)