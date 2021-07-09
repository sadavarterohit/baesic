#This file contains all the needed code for the bae-sick language

# Here are the
# CONSTANTS
from string_with_arrows import *
import string
DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS+DIGITS


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

class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details=' '):
        super().__init__(pos_start, pos_end, 'Expected Character', details)

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

        return "Error here :"+result



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

        return self

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
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD  =   'KEYWORD'
TT_EQ       =   'EQ' 
TT_NE       =   'NE'
TT_EE       =   'EE'
TT_LT       =   'LT'
TT_GT       =   'GT'
TT_GTE      =   'GTE'
TT_LTE      =   'LTE'
TT_NEWLINE  =   'NEWLINE'


KEYWORDS = [
    'VAR',
    'AND',
    'OR',
    'NOT',
    'IF',
    'THEN',
    'ELIF',
    'ELSE',
    'FOR',
    'TO',
    'STEP',
    'WHILE',
    'END'
]





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

    def matches(self, type_, value):
        return self.type==type_ and self.value==value
        

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
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char in '\n;':
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
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
            #elif self.current_char == '=':
            #    tokens.append(Token(TT_EQ, pos_start=self.pos))
            #    self.advance()
            elif self.current_char=='!':
                tok, error = self.make_not_equals()
                if error : return [],error
                tokens.append(tok)
            elif self.current_char=='=':
                tokens.append(self.make_equals())
            elif self.current_char=='<':
                tokens.append(self.make_less_than())
            elif self.current_char=='>':
                tokens.append(self.make_greater_than())


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

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()
        while self.current_char !=None and self.current_char in LETTERS_DIGITS +'_':
            id_str+=self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None
        self.advace()
        return None, ExpectedCharError(pos_start, self.pos, "'=' after !")

    def make_equals(self):
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)


###############################
##Nodes of the parse tree

class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end




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


class IfNode:
    def __init__(self, cases, else_case=None):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases)-1])[0].pos_end 

class ForNode:
    def __init__(self, var_name, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
        self.var_name_tok = var_name
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

class WhileNode:
    def __init__(self, condition_node, body_node,should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = condition_node.pos_start
        self.pos_end = body_node.pos_end

class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes

        self.pos_start  = pos_start
        self.pos_end = pos_end



# PARSE RESULT CLASS

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.advance_count+=1
        
        
    def register(self, res):
        self.advance_count+=res.advance_count
        if res.error: self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)
        

    def success(self, node):
        self.node = node
        return self

    def failure(self,error):
        if not self.error or self.advance_count==0:
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
        self.update_current_tok()
        return self.current_tok
    
    def reverse(self, amount =1 ):
        self.tok_idx -=amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx>=0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = self.statements()
        if not res.error and self.current_tok.type!=TT_EOF:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected mathematical operation"))
        return res

    ####
    # methods for the rules in our grammer

    def if_expr(self):
        res=ParseResult()
        all_cases = res.register(self.if_expr_cases('IF'))
        if res.error: return res
        cases, else_case = all_cases
        return res.success(IfNode(cases,else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, case_keyword):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, f"Expected {case_keyword}"))

        res.register_advancement()
        self.advance()

        condition= res.register(self.expr())

        if res.error: return res

        if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected THEN"))


        res.register_advancement()
        self.advance()
        
        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition,statements, True))

            if self.current_tok.matches(TT_KEYWORD,'END'):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error: return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.expr())
            if res.error: return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases('ELIF')

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TT_KEYWORD, 'ELSE'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements())
                if res.error: return res

                else_case = (statements, True)

                if self.current_tok.matches(TT_KEYWORD, 'END'):
                    res.register_advancement()
                    self.advance()
                else:
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "EXPECTED END"))

            else:
                expr = res.register(self.expr())
                if res.error: return res
                else_case = (expr, False)
        return res.success(else_case)


    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(TT_KEYWORD, 'ELIF'):
            all_cases = res.register(self.if_expr_b())
            if res.error : return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error: return res

        return res.success((cases, else_case))

        


    def for_expr(self):
        res=ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'FOR'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected FOR"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected IDENTIFIER"))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()
        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ="))
        
        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error: return res
        
        if not self.current_tok.matches(TT_KEYWORD,'TO'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected TO"))

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error: return res
        
        step_value=None
        if self.current_tok.matches(TT_KEYWORD, 'STEP'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error: return res

        if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected THEN"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error : return res

            if not self.current_tok.matches(TT_KEYWORD, 'END'):
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, 'Expected END'))

            res.register_advancement()
            self.advance()

            return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))


        body  = res.register(self.expr())
        if res.error:return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))
        
    def while_expr(self):
        res = ParseResult()
        if not self.current_tok.matches(TT_KEYWORD, 'WHILE'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected WHILE"))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected THEN"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error : return res

            if not self.current_tok.matches(TT_KEYWORD, 'END'):
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, 'Expected END'))

            res.register_advancement()
            self.advance()

            return res.success(WhileNode(condition, body, True))



        body = res.register(self.expr())
        if res.error: return res

        return res.success(WhileNode(condition, body, False))

    def atom(self):
        res= ParseResult()
        tok = self.current_tok

        if(tok.type in (TT_INT, TT_FLOAT)):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif (tok.type == TT_IDENTIFIER):
            
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))
            

        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)

            else:
                
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected )"))
        elif tok.matches(TT_KEYWORD, 'IF'):
            if_expr = res.register(self.if_expr())
            if res.error : return res
            return res.success(if_expr)

        elif tok.matches(TT_KEYWORD, 'FOR'):
            for_expr = res.register(self.for_expr())
            if res.error : return res
            return res.success(for_expr)
        elif tok.matches(TT_KEYWORD, 'WHILE'):
            while_expr = res.register(self.while_expr())
            if res.error : return res
            return res.success(while_expr)

        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int or float, +,- or ( "))

    def power(self):
        return self.bin_op(self.atom, (TT_POW, ), self.factor)

    def factor(self):
        res= ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())

            if res.error :
                return res
            return res.success(UnaryOpNode(tok, factor))   
        return self.power()


    def term(self):
        return self.bin_op(self.factor, (TT_MUL,TT_DIV))

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'NOT'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error : return res
            return res.success(UnaryOpNode(op_tok, node))
        
        node = res.register(self.bin_op(self.arith_expr,(TT_EE, TT_NE, TT_LT, TT_GT,TT_LTE, TT_GTE)))
        if res.error:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected int or float or +,-,( or NOT"))
        
        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def expr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'VAR'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER : 
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end, "Expected identifier after VAR"))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected '='"))

            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())

            if res.error : return res
            return res.success(VarAssignNode(var_name,expr))



        node=res.register( self.bin_op(self.comp_expr, ((TT_KEYWORD, "AND"), (TT_KEYWORD,"OR"))))
        if res.error : return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'VAR', int or float or something"))
        return res.success(node)
    
    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

        statement = res.register(self.expr())
        if res.error : return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count ==0:
                more_statements=False
            
            if not more_statements: break

            statement = res.try_register(self.expr())
            
            if not statement:
                self.reverse(res.to_reverse_count)
                #because when we call the reverse method above, we're likely to advance a few times, gotta get the pointer back where needed
                more_statements=False
                continue
            statements.append(statement)

        return res.success(ListNode(statements, pos_start, self.current_tok.pos_end.copy()))






    
    #since the rule of term and expr and similar, just use one common one
    def bin_op(self, func_a, ops, func_b=None):
        if func_b==None:
            func_b=func_a
        res = ParseResult()
        left = res.register(func_a())
        

        if res.error:return res        
        
    
        while(self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
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

    def get_comparison_eq(self,other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context)  , None

    
    def get_comparison_ne(self,other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context)  , None

    def get_comparison_lt(self,other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context)  , None

    def get_comparison_lte(self,other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context)  , None


    def get_comparison_gt(self,other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context)  , None

    def get_comparison_gte(self,other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context)  , None


    def anded_by(self,other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context)  , None


    def ored_by(self,other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context)  , None

    def notted(self):
        return Number(1 if self.value==0 else 0).set_context(self.context) , None
    
    def is_true(self):
        return self.value!=0

    def __repr__(self):
        return str(self.value)

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start,self.pos_end)
        copy.set_context(self.context)
        return copy


#LIST CLASS, CUZ WE'RE USING IT
class List:
    def __init__(self, elements):
        self.elements = elements
        self.set_context()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self 

    def __repr__(self) -> str:
        return f'[{", ".join([str(x) for x in self.elements])}]'
        





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
    
    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTError(node.pos_start, node.pos_end, f"'{var_name}' is not defined", context))
        value=value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res=RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error : return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

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
        elif node.op_tok.type == TT_EE:
            result,error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_NE:
            result,error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_LT:
            result,error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_GT:
            result,error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_LTE:
            result,error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GTE:
            result,error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TT_KEYWORD,'AND'):
            result,error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD,'OR'):
            result,error = left.ored_by(right)

        if error:
            return res.failure(error)
        

        return res.success(result.set_pos(node.pos_start, node.pos_end))
        

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node,context))
        if res.error : return res

        error = None

        if node.op_tok.type == TT_MINUS:           
            number, error = number.multiplied_to(Number(-1))
        elif node.op_tok.matches(TT_KEYWORD,'NOT'):
            number, error =number.notted()
        
        if error:
            return res.failure(error)


        return res.success(number.set_pos(node.pos_start, node.pos_end))
    def visit_IfNode(self, node, context):
        res=RTResult()

        for condition, expr, should_return_null in node.cases:
            condition_value =res.register(self.visit(condition, context))
            if res.error: return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                return res.success(Number.null if should_return_null else expr_value)

        if node.else_case:
            expr, should_return_null = node.else_case
            else_value = res.register(self.visit(expr, context))
            if res.error:return res
            return res.success(Number.null if should_return_null else else_value)

        return res.success(Number.null)

    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

        start_value =  res.register(self.visit(node.start_value_node, context))
        if res.error: return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error: return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))

            if res.error: return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >=0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda:i > end_value.value
        
        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i+=step_value.value

            elements.append(res.register(self.visit(node.body_node, context)))

            if res.error: return res
        return res.success(Number.null if node.should_return_null else List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))


    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements=[]        
        
        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error : return res

            if not condition.is_true():
                
                break

            elements.append(res.register(self.visit(node.body_node, context)))
            if res.error: return res

        return res.success(Number.null if node.should_return_null else List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.error : return res

        return res.success(List(elements).set_context(context).set_pos(node.pos_start, node))


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
