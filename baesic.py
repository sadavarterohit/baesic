#This file contains all the needed code for the bae-sick language

# Here are the
# CONSTANTS
from string_with_arrows import *
DIGITS = '0123456789'

#HERE are the 
# ERRORS

class Error:
    def __init__(self,pos_start, pos_end, error_name, details):
        self.error_name = error_name
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.details = details
    
    def as_string(self):
        result = f'{self.error_name} : {self.details}'
        result +=' '   
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln+1}'
        result+= '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character' , details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'RunTime Error', details)
        self.context = context
    
    def as_string(self):
        
        result = self.generate_traceback()
        result += f'{self.error_name} : {self.details}'
        result +=' '   
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln+1}'
        result+= '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        context = self. context

        while context:
            result = f'File {pos.fn}, line {str(pos.ln +1)}, in {context.display_name}\n' + result
            pos = context.parent_entry_pos
            context = context.parent    

        return result



# Here is the 
# Position class

class Position:
    def __init__(self, index, ln, col, fn, ftxt):
        self.index = index
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.index += 1
        self.col += 1

        if current_char=='\n':
            self.ln+=1
            self.col =0

    def copy(self):
        return Position(self.index, self.ln, self.col, self.fn, self.ftxt)


    
#Here are the 
# TOKEN TYPES

TT_INT       = 'INT'
TT_FLOAT     = 'FLOAT'
TT_PLUS      = 'PLUS'
TT_MINUS     = 'MINUS'
TT_MUL       = 'MUL'
TT_DIV       = 'DIV'
TT_POW       = 'POW'
TT_LPAREN    = 'LPAREN'
TT_RPAREN    = 'RPAREN'
TT_EOF       = 'EOF'





class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def __repr__(self):
        if self.value : return f'{self.type}:{self.value}'
        return f'{self.type}'
        

## HERE IS THE

# LEXER

class Lexer:

    def __init__(self,fn,text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char=None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None
        
    def make_tokens(self):
        tokens = []
  
        while self.current_char!= None:
            if self.current_char in ' \t':
                self.advance()
                
            elif self.current_char in DIGITS:
                
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None


    def make_number(self):
        
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()
        
        while (self.current_char!=None and self.current_char in DIGITS +'.'):
            
            if self.current_char == '.':
                if dot_count == 1 : break
                dot_count+=1
                num_str+='.'
            else:
                num_str += self.current_char

            self.advance()


        if dot_count ==0:
            return(Token(TT_INT, int(num_str), pos_start, self.pos))
        else:
            return(Token(TT_FLOAT, float(num_str), pos_start, self.pos))

###############################
##Nodes of the parse tree

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


#Unary Operations node
class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'



#Binary operation node
class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok} , {self.right_node})'

# PARSE RESULT CLASS

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        
    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self,error):
        self.error=error
        return self


# RUNTIME RESULT CLASS

class RTResult:
    def __init__(self):
        self.value=None
        self.error = None

    def register(self,res):
        if res.error : self.error = res.error
        return res.value
    
    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self



## PARSER CLASS
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1

        self.advance()

    def advance(self):
        self.tok_idx+=1
        if(self.tok_idx < len(self.tokens)):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type!=TT_EOF:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected mathematical operation"))
        return res

    ####
    # methods for the rules in our grammer

    def atom(self):
        res= ParseResult()
        tok = self.current_tok

        if(tok.type in [TT_INT, TT_FLOAT]):
            res.register(self.advance())
            return res.success(NumberNode(tok))
            

        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)

            else:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected )"))

        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int or float"))

    def power(self):
        return self.bin_op(self.atom, [TT_POW], self.factor)

    def factor(self):
        res= ParseResult()
        tok = self.current_tok

        if tok.type in [TT_PLUS, TT_MINUS]:
            res.register(self.advance())
            factor = res.register(self.factor())

            if res.error : return res
            return res.success(UnaryOpNode(tok, factor))   


        return self.power()

    


    def term(self):
        return self.bin_op(self.factor, [TT_MUL,TT_DIV])

    def expr(self):
        return self.bin_op(self.term, [TT_PLUS,TT_MINUS])

    #since the rule of term and expr and similar, just use one common one
    def bin_op(self, func_a, ops, func_b=None):
        if func_b==None:
            func_b=func_a
        res = ParseResult()
        left = res.register(func_a())
        

        if res.error:return res        

        while(self.current_tok.type in ops):
            op_tok = self.current_tok
            res.register(self.advance())
            right=res.register(func_b())

            if res.error: return res

            left= BinOpNode(left, op_tok, right)

        return res.success(left)

#Number class cuz it's a form of data
class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self 

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context) , None

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context)  ,None

    def multiplied_to(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context)  , None

    def divided_by(self, other):
        if isinstance(other, Number):
            if other.value == 0 :
                return None, RTError(other.pos_start, other.pos_end, 'Division by zero', self.context)


            return Number(self.value / other.value).set_context(self.context)  , None

    def power_of(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context)  , None


    def __repr__(self):
        return str(self.value)

# HERE IS CONTEXT
class Context:
    def __init__(self, display_name, parent = None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent= parent
        self.parent_entry_pos = parent_entry_pos



# HERE WE HAVE
# INTERPRETERRRR
class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        #now if the node is a binary op node, it automatically uses method binop (class) 
        # and if there is one called number, makes number node 
        method = getattr(self, method_name, self.no_visit_method)
        #methodname to which you wanna go to, and default method

        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node, context):
        return RTResult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))
    
    def visit_BinOpNode(self, node, context):
        res= RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res

        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multiplied_to(right)
        elif node.op_tok.type == TT_DIV:
            result,error = left.divided_by(right)
        elif node.op_tok.type == TT_POW:
            result,error = left.power_of(right)

        if error:
            return res.failure(error)

        return res.success(result.set_pos(node.pos_start, node.pos_end))
        

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node.context))

        error = None

        if node.op_tok.type == TT_MINUS:           
            number, error = number.multiplied_to(Number(-1))
        
        if error:
            return res.failure(error)


        return res.success(number.set_pos(node.pos_start, node.pos_end))


#######
#RUN


def run(fn, text):
    lexer = Lexer(fn,text)
    tokens, error = lexer.make_tokens()

    #print("Tokens")
    #print(tokens)
    if error :return None, error
    parser = Parser(tokens)
    ast = parser.parse()

    if ast.error : return None, error
    #print("\nAST :")
    #print(ast)
    interpreter = Interpreter()

    context=Context('<program>')
    result = interpreter.visit(ast.node, context)


    return result.value, result.error
