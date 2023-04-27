from interpreter import Lexer, Parser
import sys
from shell import shell


def main():
    debug = False
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            if sys.argv[2] == "debug":
                debug = True
        FILE = sys.argv[1]
        lexer = Lexer(file=FILE)
        tokens = lexer.tokenize()
        parser = Parser(debug=debug)
        parser.parse(tokens)
    else:
        shell()


if __name__ == "__main__":
    main()
