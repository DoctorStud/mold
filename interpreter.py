from enum import Enum

SYMBOLS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


class Tok(Enum):
    RPAREN = "RPAREN"
    LPAREN = "LPAREN"
    COMMA = "COMMA"
    EQUAL = "EQUAL"
    RULE = "RULE"
    STRING = "STRING"

    def __str__(self):
        return self.value


class Token:
    def __init__(self, type_: Tok, value=None):
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
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def tokenize(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char in " \t\n ":
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
            elif self.current_char in SYMBOLS:
                string = self.make_string()
                if string == "rule":
                    tokens.append(Token(Tok.RULE))
                else:
                    tokens.append(Token(Tok.STRING, string))
        return tokens

    def make_string(self):
        string: str = self.current_char
        self.advance()
        while self.current_char is not None and self.current_char in SYMBOLS:
            string += self.current_char
            self.advance()
        return string


class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.index = -1
        self.current_token = None
        self.advance()

    def advance(self):
        self.index += 1
        self.current_token = (
            self.tokens[self.index] if self.index < len(self.tokens) else None
        )

    def parse(self):
        pass
