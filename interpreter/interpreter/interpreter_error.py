class InvalidFunctionCall(Exception):
    def __init__(self, id) -> None:
        super().__init__(f"{id} is not a function.")

class FunctionDoesNotExist(Exception):
    def __init__(self, id) -> None:
        super().__init__(f"Function: {id} does not exist")