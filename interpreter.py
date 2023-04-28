from enum import Enum
from expr import Var, Fun, Sym, Op, Def
from collections import OrderedDict

SYMBOLS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ñç"
OPERATORS = "/*-+?!#€%|¬^&<>"


class ExpectedTokenError(Exception):
    def __init__(self, token):
        super().__init__(f"Expected token: {token}")


class MissingOperandError(Exception):
    def __init__(self, side):
        super().__init__(f"Missing {side} operand")


class Tok(Enum):
    EOL = "EOL"
    COMMENT = "COMMENT"
    RPAREN = "RPAREN"
    LPAREN = "LPAREN"
    COMMA = "COMMA"
    EQUAL = "EQUAL"
    DEF = "DEF"
    STRING = "STRING"
    OPERATOR = "OPERATOR"
    APPLY = "APPLY"
    DOT = "DOT"
    LSQBRACKET = "LSQBRACKET"
    RSQBRACKET = "RSQBRACKET"
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
    def __init__(self, file=None, lines=None):
        if file:
            self.file = file
            try:
                with open(self.file) as f:
                    self.lines = f.readlines()
            except FileNotFoundError as e:
                raise e
        elif lines:
            self.lines = lines
        self.current_line = None
        self.char_pos = -1
        self.current_char = None
        self.tokens = []

    def advance(self):
        self.char_pos += 1
        self.current_char = self.current_line[self.char_pos] if self.char_pos < len(
            self.current_line) else None

    def tokenize(self):
        for line in self.lines:
            self.current_line = line
            self.char_pos = -1
            self.advance()
            self.tokens.extend(self.tokenize_line())
        return self.tokens

    def tokenize_line(self):
        tokens = []
        while self.current_char:
            if self.current_char in "\n":
                return tokens
            elif self.current_char in " \t":
                self.advance()
            elif self.current_char == "(":
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
            elif self.current_char == "]":
                tokens.append(Token(Tok.RSQBRACKET))
                self.advance()
            elif self.current_char == "[":
                tokens.append(Token(Tok.LSQBRACKET))
                self.advance()
            elif self.current_char == ":":
                self.advance()
                if self.current_char == "=":
                    tokens.append(Token(Tok.DEF))
                    self.advance()
                else:
                    print(f"Error")
                    break
            elif self.current_char == "/":
                self.advance()
                if self.current_char == "/":
                    return tokens
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
                print(
                    f"Invalid character: '{self.current_char}' at ({self.lines.index(self.current_line)}, {self.char_pos})")
                break
        return tokens

    def make_string(self):
        string = ""
        while self.current_char and self.current_char in SYMBOLS:
            string += self.current_char
            self.advance()
        return string


class Parser:
    def __init__(self, debug=False):
        self.defs = {}
        self.debug = debug
        self.last_result = None
        self.result = OrderedDict()

    def output(self):
        for body, result in self.result.items():
            print(f"{body[0]} => {result}")

    def parse(self, tokens):
        if not tokens:
            return self.result
        self.tokens = iter(tokens)
        self.next_token = None
        self.current_token = None
        self.list = []
        self.advance()
        while self.next_token:
            self.list.append(self.expr())
        self.output()
        return self.result

    def advance(self):
        self.current_token, self.next_token = self.next_token, next(
            self.tokens, None)

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
            elif self.check_type(Tok.DEF):
                self.advance()
                return self._def(name)
            else:
                return self.sym(name)
        elif self.check_type(Tok.LBRACKET):
            return self.var()
        elif self.check_type(Tok.OPERATOR):
            return self.op()
        elif self.check_type(Tok.APPLY):
            self.advance()
            strat = None
            name = self.next_token.value
            self.expect(Tok.STRING)
            if self.check_type(Tok.LSQBRACKET):
                self.advance()
                strat = self.next_token.value
                self.expect(Tok.STRING)
                self.expect(Tok.RSQBRACKET)
            return self.apply(name, strat=strat)
        elif self.check_type(Tok.LPAREN):
            self.advance()
            while self.next_token:
                if self.next_token.type == Tok.RPAREN:
                    self.advance()
                    return self.list[-1]
                self.list.append(self.expr())
            return self.list[-1]

    def var(self):
        self.advance()
        var = self.next_token
        self.expect(Tok.STRING)
        self.expect(Tok.RBRACKET)
        return Var(var.value)

    def sym(self, name):
        return Sym(name)

    def op(self):
        if len(self.list) == 0:
            raise MissingOperandError("left")
        left_op = self.list[-1]
        op = self.next_token
        self.advance()
        right_op = self.expr()
        if right_op is None:
            raise MissingOperandError("right")
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
            elif self.next_token.type == Tok.OPERATOR:
                args.pop()
            expr = self.expr()
            self.list.append(expr)
            args.append(expr)
        return args

    def _def(self, name):
        head = self.expr()
        while self.check_type(Tok.OPERATOR):
            self.list.append(head)
            head = self.expr()
        self.expect(Tok.EQUAL)
        body = self.expr()
        while self.check_type(Tok.OPERATOR):
            self.list.append(body)
            body = self.expr()
        _def = Def(name, head, body)
        self.defs[name] = _def
        return _def

    def apply(self, name, strat):
        if self.next_token is None:
            body = self.last_result
        elif self.check_type(Tok.DEF) or self.check_type(Tok.APPLY):
            body = self.last_result
        else:
            body = self.expr()
        while self.check_type(Tok.OPERATOR):
            self.list.append(body)
            body = self.expr()
        self.result[(body, name)] = self.defs[name].apply(
            body, strat=strat, debug=self.debug)
        self.last_result = self.result[(body, name)]
        return self.result[(body, name)]
