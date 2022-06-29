from __future__ import division
from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional,
                    ZeroOrMore, Forward, nums, alphas, oneOf)

import tweepy
import math
import operator
import time

#login with twitter api
bearer_token='AAAAAAAAAAAAAAAAAAAAADfyJQEAAAAAvgA5ggHQtAfCt5B2On0FfrFtOvY%3DLRlDvdFpXMnq9b0hgWZyittwutMAYlWLpWsdHUJsYPo2yJyq2X'
auth = tweepy.OAuthHandler('eKYd3WcAqgS1hAcHJzL7Snaon', 'KYF9DD72TfotTnNoqpp7tQgfEsHgvDOBEzvyVIc0iDg8PREgKQ')
auth.set_access_token('1324633951864979457-nOce2RwBcs6gs5fTeGDUwz68YkswgB', 'CoYJkyRRypcdN1jC8askKNpmC5mx9VrxUmrlNYFpCDGMy')
api = tweepy.API(auth)





#class containing all calculation methods
class NumericStringParser(object):
    '''
    Most of this code comes from the fourFn.py pyparsing example

    '''



    def pushFirst(self, strg, loc, toks):
        self.exprStack.append(toks[0])



    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == '-':
            self.exprStack.append('unary -')



    def __init__(self):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(Word("+-" + nums, nums) +
                          Optional(point + Optional(Word(nums))) +
                          Optional(e + Word("+-" + nums, nums)))
        ident = Word(alphas, alphas + nums + "_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        pi = CaselessLiteral("PI")
        expr = Forward()
        atom = ((Optional(oneOf("- +")) +
                 (ident + lpar + expr + rpar | pi | e | fnumber).setParseAction(self.pushFirst))
                | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
                ).setParseAction(self.pushUMinus)
        # by defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + \
            ZeroOrMore((expop + factor).setParseAction(self.pushFirst))
        term = factor + \
            ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
        expr << term + \
            ZeroOrMore((addop + term).setParseAction(self.pushFirst))
        # addop_term = ( addop + term ).setParseAction( self.pushFirst )
        # general_term = term + ZeroOrMore( addop_term ) | OneOrMore( addop_term)
        # expr <<  general_term
        self.bnf = expr
        # map operator symbols to corresponding arithmetic operations
        epsilon = 1e-12
        self.opn = {"+": operator.add,
                    "-": operator.sub,
                    "*": operator.mul,
                    "/": operator.truediv,
                    "^": operator.pow}



        self.fn = {"sin": math.sin,
                   "cos": math.cos,
                   "tan": math.tan,
                   "exp": math.exp,
                   "asin": math.asin,
                   "acos": math.acos,
                   "atan": math.atan2,
                   "sqrt": math.sqrt,
                   "log": math.log,
                   "factorial": math.factorial,
                   "gamma": math.gamma,
                   "abs": abs,
                   "trunc": lambda a: int(a),
                   "round": round,
                   "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0,
                   }



    def evaluateStack(self, s):
        op = s.pop()
        if op == 'unary -':
            return -self.evaluateStack(s)
        if op in "+-*/^":
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.opn[op](op1, op2)
        elif op == "PI":
            return math.pi  # 3.1415926535
        elif op == "E":
            return math.e  # 2.718281828
        elif op in self.fn:
            return self.fn[op](self.evaluateStack(s))
        elif op[0].isalpha():
            return 0
        else:
            return float(op)



    def eval(self, num_string, parseAll=True):
        self.exprStack = []
        results = self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val


nsp = NumericStringParser()





FILE_NAME = 'last_seen_id.txt'



def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return



def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id




def reply_to_tweets():
    print('retrieving and replying to tweets...', flush=True)
    # DEV NOTE: use 1060651988453654528 for testing.
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    # NOTE: We need to use tweet_mode='extended' below to show
    # all full tweets (with full_text). Without it, long tweets
    # would be cut off.
    mentions = api.mentions_timeline(
                        last_seen_id,
                        tweet_mode='extended')



    for mention in reversed(mentions):
        exp = mention.full_text.lower()
        print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if '#calci' in mention.full_text.lower():
            print('found tweet', flush=True)
            exp = exp.replace('@calcibot ', '')
            exp = exp.replace('\\', '')
            exp = exp.replace('#calci', '')
            # get the mathematical expression and reply with solution
            reply = nsp.eval(exp)
            print(exp)
            print('responding back...', flush=True)
            print(str(reply))
            api.update_status('@' + mention.user.screen_name + ' '+ exp +'= '+ str(reply), mention.id)


        


while True:

    reply_to_tweets()
    time.sleep(10)