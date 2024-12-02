from __future__ import annotations

from truffle_sdk import AppState, tool, state
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

@state()
class State(AppState):
    memory: int = 0
    history: List[Operation] = []
    cursor: int = -1

class Operation(BaseModel, ABC):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[int] = None
    
    @abstractmethod
    def describe(self) -> str:
        pass

    @abstractmethod
    def execute(self) -> None:
        pass
    
class Calculator:
    def __init__(self, state: State):
        self.state = state

    def get_current_result(self):
        if 0 <= self.state.cursor < len(self.state.history):
            return self.state.history[self.state.cursor].result
        else:
            return self.state.memory  # Return memory when there's no history

    def execute(self, op: Operation):
        op.execute()
        # Trim history if we've undone and are adding new operations
        if self.state.cursor < len(self.state.history) - 1:
            self.state.history = self.state.history[:self.state.cursor + 1]
        self.state.history.append(op)
        self.state.cursor += 1
        self.state.memory = op.result  # Update memory with the result
        return op.result

    def undo(self):
        if self.state.cursor >= 0:
            self.state.cursor -= 1
            if self.state.cursor >= 0:
                # Update memory to the result at the new cursor position
                self.state.memory = self.state.history[self.state.cursor].result
            else:
                self.state.memory = 0  # Reset memory if no operations left
            return True
        else:
            print("No more operations to undo.")
            return False

    def redo(self):
        if self.state.cursor < len(self.state.history) - 1:
            self.state.cursor += 1
            # Update memory to the result at the new cursor position
            self.state.memory = self.state.history[self.state.cursor].result
            return True
        else:
            print("No more operations to redo.")
            return False

class AddOperation(Operation):
    a: int
    b: int
    
    def execute(self) -> None:
        self.result = self.a + self.b
        
    def describe(self) -> str:
        return f"{self.a} + {self.b} = {self.result}"

class SubtractOperation(Operation):
    a: int
    b: int
    
    def execute(self) -> None:
        self.result = self.a - self.b
        
    def describe(self) -> str:
        return f"{self.a} - {self.b} = {self.result}"

class MultiplyOperation(Operation):
    a: int
    b: int
    
    def execute(self) -> None:
        self.result = self.a * self.b
        
    def describe(self) -> str:
        return f"{self.a} * {self.b} = {self.result}"

class DivideOperation(Operation):
    a: int
    b: int
    result: Optional[float] = None
    
    def execute(self) -> None:
        self.result = self.a / self.b
        
    def describe(self) -> str:
        return f"{self.a} / {self.b} = {self.result}"

class PowerOperation(Operation):
    base: int
    exponent: int
    
    def execute(self) -> None:
        self.result = self.base ** self.exponent
        
    def describe(self) -> str:
        return f"{self.base} ^ {self.exponent} = {self.result}"

class ModuloOperation(Operation):
    a: int
    b: int
    
    def execute(self) -> None:
        self.result = self.a % self.b
        
    def describe(self) -> str:
        return f"{self.a} % {self.b} = {self.result}"

class FloorDivideOperation(Operation):
    a: int
    b: int
    
    def execute(self) -> None:
        self.result = self.a // self.b
        
    def describe(self) -> str:
        return f"{self.a} // {self.b} = {self.result}"

class AbsoluteOperation(Operation):
    x: int
    
    def execute(self) -> None:
        self.result = abs(self.x)
        
    def describe(self) -> str:
        return f"|{self.x}| = {self.result}"
    

state = State()
calculator = Calculator(state)

@tool()
def add(a: int, b: int) -> int:
    op = AddOperation(a=a, b=b)
    calculator.execute(op)
    return calculator.get_current_result()

@tool()
def subtract(a: int, b: int) -> int:
    op = SubtractOperation(a=a, b=b)
    calculator.execute(op)
    return calculator.get_current_result()

@tool()
def multiply(a: int, b: int) -> int:
    op = MultiplyOperation(a=a, b=b)
    calculator.execute(op)
    return calculator.get_current_result()

@tool()
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    op = DivideOperation(a=a, b=b)
    calculator.execute(op)
    return calculator.get_current_result()

@tool()
def power(base: int, exponent: int) -> int:
    op = PowerOperation(base=base, exponent=exponent)
    calculator.execute(op)
    return calculator.get_current_result()

@tool()
def modulo(a: int, b: int) -> int:
    if b == 0:
        raise ValueError("Cannot compute modulo with zero")
    op = ModuloOperation(a=a, b=b)
    calculator.execute(op)
    return calculator.get_current_result()

@tool()
def floor_divide(a: int, b: int) -> int:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    op = FloorDivideOperation(a=a, b=b)
    calculator.execute(op)
    return calculator.get_current_result()

@tool()
def absolute(x: int) -> int:
    op = AbsoluteOperation(x=x)
    calculator.execute(op)
    return calculator.get_current_result()

@tool()
def undo_operation() -> str:
    if calculator.undo():
        return f"Undo successful. Current result: {calculator.get_current_result()}"
    else:
        return "No operation to undo."

@tool()
def redo_operation() -> str:
    if calculator.redo():
        return f"Redo successful. Current result: {calculator.get_current_result()}"
    else:
        return "No operation to redo."