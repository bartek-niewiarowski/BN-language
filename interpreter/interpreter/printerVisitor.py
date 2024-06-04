from .visitor import Visitor
from ..parser.syntax_tree import *

class PrintVisitor(Visitor):
    def __init__(self):
        self.indent_level = 0

    def _print_indent(self, text):
        print( "   " * self.indent_level  + text)

    def visit_program(self, program: Program):
        self._print_indent(f"Program at {program.position}")
        self.indent_level += 1
        for include in program.includes:
            include.accept(self)
        for function in program.functions.values():
            function.accept(self)
        self.indent_level -= 1

    def visit_function_definition(self, node: FunctionDefintion):
        self._print_indent(f"Function \"{node.name}\" at {node.position}")
        self.indent_level += 1
        params = ", ".join(obj for obj in node.parameters)
        self._print_indent(f"With parameters: \"{params}\"")
        node.statements.accept(self)
        self.indent_level -= 1

    def visit_include_statement(self, node: IncludeStatement):
        objects_names = ", ".join(obj for obj in node.objects_names)
        self._print_indent(f"Include {node.library_name} with objects {objects_names} at {node.position}")

    def visit_lambda_expression(self, node: LambdaExpression):
        self._print_indent(f"Lambda {node.variable_name} at {node.position}")
        self.indent_level += 1
        for stmt in node.statements:
            stmt.accept(self)
        self.indent_level -= 1

    def visit_identifier(self, node: Identifier):
        self._print_indent(f"Identifier \"{node.name}\" at {node.position}")

    def visit_parameter(self, node: Parameter):
        self._print_indent(f"Parameter \"{node.name}\" at {node.position}")

    def visit_return_statement(self, node: ReturnStatement):
        self._print_indent(f"ReturnStatement at {node.position}")
        self.indent_level += 1
        node.statement.accept(self)
        self.indent_level -= 1

    def visit_if_statement(self, node: IfStatement):
        self._print_indent(f"If statement at {node.position} with condition:")
        self.indent_level += 1
        node.condition.accept(self)
        self._print_indent("Then:")
        self.indent_level += 1
        for stmt in node.statements:
            stmt.accept(self)
        self.indent_level -= 1
        if node.else_statement:
            self._print_indent("Else:")
            self.indent_level += 1
            for stmt in node.else_statement:
                stmt.accept(self)
            self.indent_level -= 1
        self.indent_level -= 1

    def visit_while_statement(self, node: WhileStatement):
        self._print_indent(f"While statement at {node.position} with condition:")
        self.indent_level += 1
        node.condition.accept(self)
        self._print_indent("Do:")
        self.indent_level += 1
        for stmt in node.statements:
            stmt.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1

    def visit_break_statement(self, node: BreakStatement):
        self._print_indent(f"BreakStatement at {node.position}")

    def visit_or_expression(self, node: OrExpression):
        self._print_indent(f"OrExpression at {node.position}")
        self.indent_level += 1
        for expr in node.nodes:
            expr.accept(self)
        self.indent_level -= 1

    def visit_and_expression(self, node: AndExpression):
        self._print_indent(f"AndExpression at {node.position}")
        self.indent_level += 1
        for expr in node.nodes:
            expr.accept(self)
        self.indent_level -= 1

    def visit_negation(self, node: Negation):
        self._print_indent(f"Negation of type {node.negation_type} at {node.position}")
        self.indent_level += 1
        node.node.accept(self)
        self.indent_level -= 1

    def visit_sum_expression(self, node: SumExpression):
        self._print_indent(f"SumExpression at {node.position}")
        self.indent_level += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent_level -= 1

    def visit_sub_expression(self, node: SubExpression):
        self._print_indent(f"SubExpression at {node.position}")
        self.indent_level += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent_level -= 1

    def visit_mul_expression(self, node: MulExpression):
        self._print_indent(f"MulExpression at {node.position}")
        self.indent_level += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent_level -= 1

    def visit_div_expression(self, node: DivExpression):
        self._print_indent(f"DivExpression at {node.position}")
        self.indent_level += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent_level -= 1

    def visit_equal_operation(self, node: EqualOperation):
        self._print_indent(f"EqualOperation at {node.position}")
        self.indent_level += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent_level -= 1

    def visit_not_equal_operation(self, node: NotEqualOperation):
        self._print_indent(f"NotEqualOperation at {node.position}")
        self.indent_level += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent_level -= 1

    def visit_greater_operation(self, node: GreaterOperation):
        self._print_indent(f"GreaterOperation at {node.position}")
        self.indent_level += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent_level -= 1

    def visit_greater_equal_operation(self, node:GreaterEqualOperation):
        self._print_indent(f"GreaterEqualOperation at {node.position}")
        self.indent_level += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent_level -= 1

    def visit_less_operation(self, node: LessOperation):
        self._print_indent(f"LessOperation at {node.position}")
        self.indent_level += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent_level -= 1

    def visit_less_equal_operation(self, node: LessEqualOperation):
        self._print_indent(f"LessEqualOperation at {node.position}")
        self.indent_level += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent_level -= 1

    def visit_literal_bool(self, node: LiteralBool):
        self._print_indent(f"LiteralBool {node.value} at {node.position}")

    def visit_literal_int(self, node: LiteralInt):
        self._print_indent(f"LiteralInt {node.value} at {node.position}")

    def visit_literal_float(self, node: LiteralFloat):
        self._print_indent(f"LiteralFloat {node.value} at {node.position}")

    def visit_literal_string(self, node: LiteralString):
        self._print_indent(f"LiteralString \"{node.value}\" at {node.position}")

    def visit_array(self, node: Array):
        self._print_indent(f"Array at {node.position}")
        self.indent_level += 1
        for item in node.items:
            item.accept(self)
        self.indent_level -= 1

    def visit_assignment(self, node: Assignment):
        self._print_indent(f"Assignment at {node.position}")
        self.indent_level += 1
        node.target.accept(self)
        node.value.accept(self)
        self.indent_level -= 1

    def visit_function_call(self, node: FunctionCall):
        self._print_indent(f"FunctionCall to {node.function_name} at {node.position}")
        self.indent_level += 1
        node.arguments.accept(self)
        self.indent_level -= 1

    def visit_statements(self, node: Statements):
        self._print_indent(f"Statements at {node.position}")
        self.indent_level += 1
        for stmt in node.statements:
            stmt.accept(self)
        self.indent_level -= 1
    
    def visit_function_arguments(self, element: FunctionArguments):
        return super().visit_function_arguments(element)