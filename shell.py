from interpreter import Lexer, Parser


def main():
    while True:
        text = input("> ")
        if text == "quit":
            quit()
        lexer = Lexer(text)
        print(lexer.tokenize())
        parser = Parser(lexer.tokenize())


if __name__ == "__main__":
    main()
