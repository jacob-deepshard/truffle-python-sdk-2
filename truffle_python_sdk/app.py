from typing import TYPE_CHECKING
from pydantic import BaseModel

from truffle_python_sdk.utils import tool

if TYPE_CHECKING:
    from truffle_python_sdk.client import Client

class TruffleApp(BaseModel):
    client: "Client"

    @tool()
    def save(self) -> BaseModel:
        return self

    @tool()
    def load(self, state: BaseModel):
        self.__dict__.update(state.__dict__)
