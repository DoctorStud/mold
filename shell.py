from interpreter import Lexer, Parser


def shell():
    parser = Parser()
    while True:
        line = input("> ")
        if line == "quit":
            quit()
        lexer = Lexer(lines=[line])
        tokens = lexer.tokenize()
        parser.parse(tokens)


if __name__ == "__main__":
    shell()
