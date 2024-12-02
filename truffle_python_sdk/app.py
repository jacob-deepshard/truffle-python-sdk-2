from pydantic import BaseModel

from truffle_python_sdk.utils import tool


class TruffleApp(BaseModel):

    @tool()
    def save(self) -> BaseModel:
        return self

    @tool()
    def load(self, state: BaseModel):
        self.__dict__.update(state.__dict__)
