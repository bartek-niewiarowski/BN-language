from abc import ABC, abstractmethod
from ..parser.syntax_tree import *
from .interpreter import Context
from interpreter_error import *


class Visitor(ABC):
    @abstractmethod
    def visit_program(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_function_definition(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_include_statement(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_lambda_expression(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_function_arguments(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_identfier(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_parameter(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_return_statement(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_if_statement(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_while_statement(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_break_statement(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_multi_parametr_expression(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_or_expression(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_and_expression(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_negation(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_arth_expression(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_sum_expression(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_sub_expression(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_mul_expression(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_div_expression(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_binary_operation(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_equal_operation(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_not_equal_operation(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_greater_operation(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_greater_equal_operation(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_less_operation(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_less_equal_operation(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_literal_bool(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_literal_int(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_literal_float(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_literal_string(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_array(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_assignment(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_function_call(self, element, context) -> None:
        pass

    @abstractmethod
    def visit_statements(self, element, context) -> None:
        pass


class ExecuteVisitor(Visitor):
    def visit_program(self, element, context: Context):
        pass

    def visit_function_definition(self, element: FunctionDefintion, context: Context):
        context.add_function(element.name, element)

    def visit_include_statement(self, element, context: Context):
        pass

    def visit_lambda_expression(self, element, context: Context):
        pass

    def visit_function_arguments(self, element: FunctionArguments, context: Context):
        args = [arg.accept(self, context) for arg in element.arguments]
        return args

    def visit_identfier(self, element, context) -> None:
        pass

    def visit_parameter(self, element, context) -> None:
        pass

    def visit_return_statement(self, element: ReturnStatement, context: Context) -> None:
        return element.statement.accept(self, context)

    def visit_if_statement(self, element: IfStatement, context: Context) -> None:
        if element.condition.accept(self, context):
            return element.statements.accept(self, context)
        elif element.else_statement:
            return element.else_statement.accept(self, context)

    def visit_while_statement(self, element: WhileStatement, context: Context) -> None:
        while element.condition.accept(self, context):
            if ret := element.statements.accept(self, context):
                return ret

    def visit_break_statement(self, element, context) -> None:
        pass

    def visit_multi_parametr_expression(self, element, context) -> None:
        pass

    def visit_or_expression(self, element, context) -> None:
        pass

    def visit_and_expression(self, element, context) -> None:
        pass

    def visit_negation(self, element, context) -> None:
        pass

    def visit_arth_expression(self, element, context) -> None:
        pass

    def visit_sum_expression(self, element, context) -> None:
        pass

    def visit_sub_expression(self, element, context) -> None:
        pass

    def visit_mul_expression(self, element, context) -> None:
        pass

    def visit_div_expression(self, element, context) -> None:
        pass

    def visit_binary_operation(self, element, context) -> None:
        pass

    def visit_equal_operation(self, element: EqualOperation, context: Context) -> None:
        return element.left.accept(self, context) == element.right.accept(self, context)

    def visit_not_equal_operation(self, element: NotEqualOperation, context: Context) -> None:
        return element.left.accept(self, context) != element.right.accept(self, context)

    def visit_greater_operation(self, element: GreaterOperation, context: Context) -> None:
        return element.left.accept(self, context) > element.right.accept(self, context)

    def visit_greater_equal_operation(self, element: GreaterEqualOperation, context: Context) -> None:
        return element.left.accept(self, context) >= element.right.accept(self, context)

    def visit_less_operation(self, element: LessOperation, context: Context) -> None:
        return element.left.accept(self, context) < element.right.accept(self, context)

    def visit_less_equal_operation(self, element: LessEqualOperation, context: Context) -> None:
        return element.left.accept(self, context) <= element.right.accept(self, context)

    def visit_literal_bool(self, element, context) -> None:
        pass

    def visit_literal_int(self, element, context) -> None:
        pass

    def visit_literal_float(self, element, context) -> None:
        pass

    def visit_literal_string(self, element, context) -> None:
        pass

    def visit_array(self, element, context) -> None:
        pass

    def visit_assignment(self, element, context) -> None:
        pass

    def visit_function_call(self, element: FunctionCall, context: Context) -> None:
        args = self.visit_function_arguments()
        
        function = context.get_function(element.function_name)
        if function is not None:
            if isinstance(function, FunctionDefintion):
                function_context = context.new_context()
                for arg, param in zip(args, function.parameters):
                    function_context.add_variable(param, arg)
                return function.statements.accept(self, function_context)
            else:
                raise InvalidFunctionCall(element.function_name)
        else:
            raise FunctionDoesNotExist(element.function_name)

    def visit_statements(self, element: Statements, context) -> None:
        for statement in element.statements:
            ret = statement.accept(self, context)
            if ret:
                return ret


class PrinterVisitor(Visitor):
    def visit_program(self, element) -> None:
        pass

    def visit_function_definition(self, element) -> None:
        pass

    def visit_include_statement(self, element) -> None:
        pass

    def visit_function_arguments(self, element) -> None:
        pass
