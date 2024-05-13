from abc import ABC, abstractmethod


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
