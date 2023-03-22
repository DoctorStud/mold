from enum import Enum
from mold import Var, Fun, Sym, Op, Def

SYMBOLS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ñç"
OPERATORS = "/*-+?!#€%|¬^&<>"


class ExpectedTokenError(Exception):
    def __init__(self, token):
        super().__init__(f"Expected token: {token}")


class Tok(Enum):
    RPAREN = "RPAREN"
    LPAREN = "LPAREN"
    COMMA = "COMMA"
    EQUAL = "EQUAL"
    DEF = "DEF"
    STRING = "STRING"
    OPERATOR = "OPERATOR"
    APPLY = "APPLY"
    DOT = "DOT"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"

    def __repr__(self):
        return self.value


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"{self.type}: '{self.value}'" if self.value else f"{self.type}"


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = -1
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(
            self.text) else None

    def tokenize(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char in " \t\n":
                self.advance()
            if self.current_char == "(":
                tokens.append(Token(Tok.LPAREN))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(Tok.RPAREN))
                self.advance()
            elif self.current_char == ",":
                tokens.append(Token(Tok.COMMA))
                self.advance()
            elif self.current_char == "=":
                tokens.append(Token(Tok.EQUAL))
                self.advance()
            elif self.current_char == ".":
                tokens.append(Token(Tok.DOT))
                self.advance()
            elif self.current_char == "{":
                tokens.append(Token(Tok.LBRACKET))
                self.advance()
            elif self.current_char == "}":
                tokens.append(Token(Tok.RBRACKET))
                self.advance()
            elif self.current_char == ":":
                self.advance()
                if self.current_char == "=":
                    tokens.append(Token(Tok.DEF))
                    self.advance()
                else:
                    print(f"Error")
                    break
            elif self.current_char in OPERATORS:
                tokens.append(Token(Tok.OPERATOR, self.current_char))
                self.advance()
            elif self.current_char in SYMBOLS:
                string = self.make_string()

                if string == "apply":
                    tokens.append(Token(Tok.APPLY))
                else:
                    tokens.append(Token(Tok.STRING, string))
            else:
                print(f"Invalid character: '{self.current_char}'")
                break
        return tokens

    def make_string(self):
        string = ""
        while self.current_char is not None and self.current_char in SYMBOLS:
            string += self.current_char
            self.advance()
        return string


class Parser:
    def __init__(self, tokens):
        self.tokens = iter(tokens)
        self.next_token = None
        self.current_token = None
        self.list = []
        self.advance()

    def advance(self):
        self.current_token, self.next_token = self.next_token, next(
            self.tokens, None)

    def parse(self):
        while self.next_token:
            self.list.append(self.expr())
        return self.list[-1]

    def accept(self, token_type):
        if self.next_token and self.next_token.type == token_type:
            self.advance()
            return True
        else:
            return False

    def expect(self, token_type):
        if not self.accept(token_type):
            raise ExpectedTokenError(token_type)

    def check_type(self, token_type):
        return self.next_token and self.next_token.type == token_type

    def expr(self):
        if self.check_type(Tok.STRING):
            name = self.next_token.value
            self.advance()
            if self.check_type(Tok.LPAREN):
                return self.fun(name)
            else:
                return self.sym(name)
        elif self.check_type(Tok.LBRACKET):
            return self.var()
        elif self.check_type(Tok.OPERATOR):
            return self.op()

    def var(self):
        self.advance()
        var = self.next_token
        self.expect(Tok.STRING)
        self.expect(Tok.RBRACKET)
        return Var(var.value)

    def sym(self, name):
        return Sym(name)

    def op(self,):
        print(self.list)
        left_op = self.list[-1]
        op = self.next_token
        self.advance()
        right_op = self.expr()
        return Op(left_op, op.value, right_op)

    def fun(self, name):
        self.advance()
        args = self.args()
        return Fun(name, *args)

    def args(self):
        args = []
        while self.next_token:
            if self.next_token.type == Tok.RPAREN:
                self.advance()
                return args
            elif self.next_token.type == Tok.COMMA:
                self.advance()
                continue
            expr = self.expr()
            self.list.append(expr)
            args.append(expr)
            if self.next_token.type == Tok.OPERATOR:
                args.pop()
        return args
