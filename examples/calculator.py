from truffle_python_sdk import TruffleApp, tool, Client
from typing import List
from pydantic import ConfigDict, BaseModel

class Operation(BaseModel):
    """
    Represents a calculator operation.
    """
    operation_type: str
    operands: tuple
    result: float

class CalculatorApp(TruffleApp):
    """
    A calculator app that supports basic arithmetic operations with history and memory.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    history: List[Operation] = []
    memory: float = 0.0

    @tool()
    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.
        """
        result = a + b
        self.history.append(Operation(operation_type='add', operands=(a, b), result=result))
        return result

    @tool()
    def subtract(self, a: float, b: float) -> float:
        """
        Subtract two numbers.
        """
        result = a - b
        self.history.append(Operation(operation_type='subtract', operands=(a, b), result=result))
        return result

    @tool()
    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.
        """
        result = a * b
        self.history.append(Operation(operation_type='multiply', operands=(a, b), result=result))
        return result

    @tool()
    def divide(self, a: float, b: float) -> str:
        """
        Divide two numbers.
        """
        if b == 0:
            return "Error: Cannot divide by zero."
        result = a / b
        self.history.append(Operation(operation_type='divide', operands=(a, b), result=result))
        return str(result)

    @tool()
    def power(self, a: float, b: float) -> float:
        """
        Raise a number to the power of another number.
        """
        result = a ** b
        self.history.append(Operation(operation_type='power', operands=(a, b), result=result))
        return result

    @tool()
    def modulo(self, a: float, b: float) -> float:
        """
        Calculate the modulo of two numbers.
        """
        result = a % b
        self.history.append(Operation(operation_type='modulo', operands=(a, b), result=result))
        return result

    @tool()
    def undo(self) -> float:
        """
        Undo the last operation and return the result of the previous operation.
        """
        if self.history:
            # Remove the last operation
            self.history.pop()
            # Return the result of the previous operation
            if self.history:
                return self.history[-1].result
            else:
                return 0.0  # No previous operations
        else:
            return 0.0  # History is empty

    @tool()
    def store_memory(self) -> str:
        """
        Store the result of the latest operation in memory.
        """
        if self.history:
            self.memory = self.history[-1].result
            return f"Stored {self.memory} in memory."
        else:
            return "No result to store in memory."

    @tool()
    def recall_memory(self) -> float:
        """
        Recall the value stored in memory.
        """
        return self.memory

    @tool()
    def clear_memory(self) -> str:
        """
        Clear the memory storage.
        """
        self.memory = 0.0
        return "Memory cleared."

app = CalculatorApp()

if __name__ == "__main__":
    # Start the app using the Client
    client = Client()
    client.start(
        app=app,
        mode='rest',  # Can be 'rest' or 'grpc'
        host='0.0.0.0',
        port=8000,    # Or any preferred port
        log_level='info',
        reload=False
    )
