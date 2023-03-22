from interpreter import Lexer, Parser


def main():
    parser = Parser()
    while True:
        text = input("> ")
        if text == "quit":
            quit()
        lexer = Lexer(text)
        tokens = lexer.tokenize()
        print("=> ", parser.parse(tokens))


if __name__ == "__main__":
    main()
