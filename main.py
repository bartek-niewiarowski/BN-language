import sys
from interpreter.lexer.lexer import Lexer, tokens_generator
from interpreter.source.source import Source
from interpreter.parser.parser import Parser

def main():
    if len(sys.argv) >= 0:
        #file_path = sys.argv[1]
        file_path = './tests/data/example2.bn'
        with open(file_path, 'r') as file:
            source = Source(file)
            lexer = Lexer(source)
            parser = Parser(lexer)
            result = parser.parse_program()
            pass
            

    else:
        print("Proszę uruchomić skrypt z podaniem ścieżki do pliku jako argumentu.")
        print("Przykład:")
        print("python nazwa_skryptu.py ścieżka/do/pliku")

if __name__ == "__main__":
    main()