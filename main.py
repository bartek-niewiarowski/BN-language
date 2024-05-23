import sys
from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.parser.parser import Parser
from interpreter.interpreter.executeVisitor import ExecuteVisitor
from interpreter.interpreter.printerVisitor import PrintVisitor
from interpreter.interpreter.interpreter import Context

def main():
    if len(sys.argv) >= 0:
        file_path = sys.argv[1]
        with open(file_path, 'r') as file:
            source = Source(file)
            lexer = Lexer(source)
            parser = Parser(lexer)
            visitor = ExecuteVisitor()
            printerVisitor = PrintVisitor()
            program = parser.parse_program()
            printerVisitor.visit_program(program, Context())
            a = visitor.visit_program(program, Context())
            print(a)

    else:
        print("Proszę uruchomić skrypt z podaniem ścieżki do pliku jako argumentu.")
        print("Przykład:")
        print("python nazwa_skryptu.py ścieżka/do/pliku")

if __name__ == "__main__":
    main()