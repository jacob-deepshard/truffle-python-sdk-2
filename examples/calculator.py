from truffle_python_sdk import TruffleApp, tool
from typing import List

class Operation:
    """
    Represents a calculator operation.
    """
    def __init__(self, operation_type: str, operands: tuple, result: float):
        self.operation_type = operation_type
        self.operands = operands
        self.result = result

class CalculatorApp(TruffleApp):
    """
    A calculator app that supports basic arithmetic operations with history and memory.
    """
    history: List[Operation] = []
    memory: float = 0.0

    @tool()
    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.
        """
        result = a + b
        self.history.append(Operation('add', (a, b), result))
        return result

    @tool()
    def subtract(self, a: float, b: float) -> float:
        """
        Subtract two numbers.
        """
        result = a - b
        self.history.append(Operation('subtract', (a, b), result))
        return result

    @tool()
    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.
        """
        result = a * b
        self.history.append(Operation('multiply', (a, b), result))
        return result

    @tool()
    def divide(self, a: float, b: float) -> float:
        """
        Divide two numbers.
        """
        if b == 0:
            return "Error: Cannot divide by zero."
        result = a / b
        self.history.append(Operation('divide', (a, b), result))
        return result

    @tool()
    def power(self, a: float, b: float) -> float:
        """
        Raise a number to the power of another number.
        """
        result = a ** b
        self.history.append(Operation('power', (a, b), result))
        return result

    @tool()
    def modulo(self, a: float, b: float) -> float:
        """
        Calculate the modulo of two numbers.
        """
        result = a % b
        self.history.append(Operation('modulo', (a, b), result))
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
    app.start()
