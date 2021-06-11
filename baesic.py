#This file contains all the needed code for the bae-sick language

# Here are the
# CONSTANTS

DIGITS = '0123456789'

#HERE are the 
# ERRORS

class Error:
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result = f'{self.error_name} : {self.details}'
        return result

class IllegalCharError(Error):
    def __init__(self, details):
        super().__init__('Illegeal Character', details)

#Here are the 
# TOKEN TYPES

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
#TT_INT = 'INT'




class Token:
    def __init__(self, type_, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value : return f'{self.type}:{self.value}'
        return f'{self.value}'
        

## HERE IS THE

# LEXER

class Lexer:
    def __init__(self,text):
        self.text =text
        self.pos=-1
        self.curent_char=None
        self.advance()

    def advance(self):
        self.pos+=1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def make_tokens(self):
        tokens = []
        while self.current_char!= None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
            else:
                char = self.curent_char
                self.advance()
                return [], IllegalCharError("'" + char + "'")
        return tokens, None


    def make_number(self):
        num_str = ''
        dot_count = 0

        while (self.current_char!=None and self.current_char in DIGITS +'.'):
            print(self.curent_char)
            if self.current_char == '.':
                if dot_count == 1 : break
                dot_count+=1
                num_str+='.'
            else:
                num_str += self.curent_char

            self.advance()
        if dot_count ==0:
            return(Token(TT_INT, int(num_str)))
        else:
            return(Token(TT_FLOAT, float(num_str)))

#######
#RUN


def run(text):
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()
