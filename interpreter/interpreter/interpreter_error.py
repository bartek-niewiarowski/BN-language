class InvalidFunctionCall(Exception):
    def __init__(self, id) -> None:
        super().__init__(f"{id} is not a function.")


class FunctionDoesNotExist(Exception):
    def __init__(self, id) -> None:
        super().__init__(f"Function: {id} does not exist")


class AndOperationError(Exception):
    def __init__(self, x, term):
        super().__init__()


class OrOperationError(Exception):
    def __init__(self, x, term):
        super().__init__()


class BreakException(Exception):
    """Wyjątek używany do obsługi instrukcji break w pętlach."""
    pass

class RecursionLimitExceeded(Exception):
    def __init__(self):
        super().__init__()

class MainFunctionRequired(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("Main function is required")