from interpreter import Lexer, Parser


def main():
    while True:
        text = input("> ")
        if text == "quit":
            quit()
        lexer = Lexer(text)
        tokens = lexer.tokenize()
        print(tokens)
        result = Parser(tokens).parse()
        print("Resultat: ", result)


if __name__ == "__main__":
    main()
