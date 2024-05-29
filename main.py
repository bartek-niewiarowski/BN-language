import sys
from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.parser.parser import Parser
from interpreter.interpreter.executeVisitor import ExecuteVisitor
from interpreter.interpreter.printerVisitor import PrintVisitor
from interpreter.interpreter.interpreter import Context

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r') as file:
                source = Source(file)
                lexer = Lexer(source)
                parser = Parser(lexer)
                visitor = ExecuteVisitor()
                printerVisitor = PrintVisitor()
                context = Context()
                program = parser.parse_program()
                #printerVisitor.visit_program(program, context)
                result = visitor.visit_program(program, context)
                print(result)
        except FileNotFoundError:
            print(f"Błąd: Nie znaleziono pliku '{file_path}'. Proszę sprawdzić ścieżkę i spróbować ponownie.")
        except Exception as e:
            print(f"Wystąpił błąd: {e}")
    else:
        print("Proszę uruchomić skrypt z podaniem ścieżki do pliku jako argumentu.")
        print("Przykład:")
        print("python nazwa_skryptu.py ścieżka/do/pliku")

if __name__ == "__main__":
    main()