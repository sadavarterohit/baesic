#This file contains all the needed code for the bae-sick language

# Here are the
# CONSTANTS

from number import Number

from interpreter import Interpreter

from errors import *

from nodes import *

from tokens import *

from resultnodes import *

from parserfile import Parser

from lexer import *








# HERE IS CONTEXT
class Context:
    def __init__(self, display_name, parent = None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent= parent
        self.parent_entry_pos = parent_entry_pos

        self.symbol_table = None


###SYMBOL TAABLE

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None  #for the parent functions 

    def get(self, name):
        value = self.symbols.get(name, None)
        if value ==None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


#######
#RUN

Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number.null)
global_symbol_table.set("TRUE", Number.false)
global_symbol_table.set("FALSE", Number.true)

def run(fn, text):
    lexer = Lexer(fn,text)
    tokens, error = lexer.make_tokens()

    print("Tokens")
    print(tokens)
    if error :return None, error
    parser = Parser(tokens)
    ast = parser.parse()

    if ast.error : return None, error
    print("\nAST :")
    print(ast.node)
    interpreter = Interpreter()

    context=Context('<program>')
    context.symbol_table= global_symbol_table
    result = interpreter.visit(ast.node, context)


    return result.value, result.error
