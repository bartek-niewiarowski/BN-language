from .visitor import Visitor

class PrinterVisitor(Visitor):
    def visit_program(self, element) -> None:
        pass

    def visit_function_definition(self, element) -> None:
        pass

    def visit_include_statement(self, element) -> None:
        pass

    def visit_function_arguments(self, element) -> None:
        pass