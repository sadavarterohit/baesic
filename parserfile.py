from errors import *

from resultnodes import *

from number import Number

from tokens import *

from nodes import *

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


