from abc import ABC, abstractmethod


class Visitor(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def visit_program(self, element) :
        pass

    @abstractmethod
    def visit_function_definition(self, element) :
        pass

    @abstractmethod
    def visit_include_statement(self, element) :
        pass

    @abstractmethod
    def visit_lambda_expression(self, element) :
        pass

    @abstractmethod
    def visit_function_arguments(self, element) :
        pass

    @abstractmethod
    def visit_identifier(self, element) :
        pass

    @abstractmethod
    def visit_parameter(self, element) :
        pass

    @abstractmethod
    def visit_return_statement(self, element) :
        pass

    @abstractmethod
    def visit_if_statement(self, element) :
        pass

    @abstractmethod
    def visit_while_statement(self, element) :
        pass

    @abstractmethod
    def visit_break_statement(self, element) :
        pass

    @abstractmethod
    def visit_or_expression(self, element) :
        pass

    @abstractmethod
    def visit_and_expression(self, element) :
        pass

    @abstractmethod
    def visit_negation(self, element) :
        pass

    @abstractmethod
    def visit_sum_expression(self, element) :
        pass

    @abstractmethod
    def visit_sub_expression(self, element) :
        pass

    @abstractmethod
    def visit_mul_expression(self, element) :
        pass

    @abstractmethod
    def visit_div_expression(self, element) :
        pass

    @abstractmethod
    def visit_equal_operation(self, element) :
        pass

    @abstractmethod
    def visit_not_equal_operation(self, element) :
        pass

    @abstractmethod
    def visit_greater_operation(self, element) :
        pass

    @abstractmethod
    def visit_greater_equal_operation(self, element) :
        pass

    @abstractmethod
    def visit_less_operation(self, element) :
        pass

    @abstractmethod
    def visit_less_equal_operation(self, element) :
        pass

    @abstractmethod
    def visit_literal_bool(self, element) :
        pass

    @abstractmethod
    def visit_literal_int(self, element) :
        pass

    @abstractmethod
    def visit_literal_float(self, element) :
        pass

    @abstractmethod
    def visit_literal_string(self, element) :
        pass

    @abstractmethod
    def visit_array(self, element) :
        pass

    @abstractmethod
    def visit_assignment(self, element) :
        pass

    @abstractmethod
    def visit_function_call(self, element) :
        pass

    @abstractmethod
    def visit_statements(self, element) :
        pass
