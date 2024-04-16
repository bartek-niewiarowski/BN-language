from tokens.token_type import TokenType
from tokens.token import Token
import tree
import sys

class Parser:
    def  __init__(self, tokens) -> None:
        self.tokens = tokens
        self.current_token = None
        self.position = -1
    
    def ConsumeToken(self) -> Token:
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None
        return self.current_token
    
    def CheckTokenType(self, type) -> bool:
        return self.current_token.type == type
    
    def MustBe(self, type):
        pass
    
    def ParseFunctionDefinition(self):
        if not self.CheckTokenType(TokenType.DEF):
            return None
        else:
            self.ConsumeToken()
    
    def ParseProgram(self):
        functions = {}
        while funDef := self.ParseFunctionDefinition():
            if name := funDef in functions:
                pass
                #throw exception
            else:
                functions[name] = funDef
        return tree.Program(functions)