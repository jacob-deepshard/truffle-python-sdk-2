from typing import Literal
from truffle_python_sdk.app import TruffleApp


class Client:
    truffle_magic_number = 18008

    def start(
        self,
        app: TruffleApp,
        mode: Literal["grpc", "rest"] = "rest",
        host: str = "0.0.0.0",
        port: int = None,
        log_level: str = "info",
        reload: bool = False,
    ):
        app.client = self
        
        if mode == "grpc":
            if port is None:
                port = 50051  # Default gRPC port
            self._start_grpc_server(app, host, port, log_level)
        elif mode == "rest":
            if port is None:
                port = 8000  # Default REST port
            self._start_rest_server(app, host, port, log_level, reload)
        else:
            raise ValueError(f"Invalid mode: {mode}")

    def _get_tools(self, app: TruffleApp):
        import inspect
        from pydantic import BaseModel

        tools = []
        for attr_name in dir(app):
            attr = getattr(app, attr_name)
            if callable(attr) and hasattr(attr, "__truffle_tool__"):
                tool_name = attr.__truffle_tool__["name"]
                sig = inspect.signature(attr)
                parameters = list(sig.parameters.values())[1:]  # Exclude 'self'
                return_type = sig.return_annotation

                # Collect parameter info
                param_list = []
                fields = {}
                for param in parameters:
                    param_annotation = (
                        param.annotation
                        if param.annotation != inspect.Parameter.empty
                        else str
                    )
                    param_list.append(
                        {
                            "name": param.name,
                            "annotation": param_annotation,
                        }
                    )
                    fields[param.name] = (param_annotation, ...)

                # Create RequestModel if necessary
                RequestModel = None
                if fields:
                    RequestModel = type(
                        f"{stringcase.capitalize(tool_name)}Request",
                        (BaseModel,),
                        fields,
                    )

                tools.append(
                    {
                        "name": tool_name,
                        "function": attr,
                        "parameters": param_list,
                        "return_type": return_type,
                        "request_model": RequestModel,
                    }
                )

        return tools

    def _start_grpc_server(self, app: TruffleApp, host: str, port: int, log_level: str):
        from ._utils import start_grpc_server

        # Extract tools
        tools = self._get_tools(app)
        start_grpc_server(tools, app, host, port, log_level)

    def generate_proto_files(self, app: TruffleApp):
        from ._utils import generate_proto_file

        # Extract tools
        tools = self._get_tools(app)
        generate_proto_file(tools)

    def _start_rest_server(
        self,
        app: TruffleApp,
        host: str,
        port: int,
        log_level: str,
        reload: bool,
    ):
        import uvicorn
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        from typing import Callable

        fastapi_app = FastAPI()

        # Register tool endpoints
        for tool_name, attr, RequestModel in self._get_tools(app):

            def create_endpoint(func: Callable, request_model):
                async def endpoint(request_data: request_model = None):
                    kwargs = request_data.dict() if request_data else {}
                    result = func(app, **kwargs)
                    return JSONResponse(content={"result": result})

                return endpoint

            endpoint_func = create_endpoint(attr, RequestModel)
            fastapi_app.post(f"/{tool_name}")(endpoint_func)

        uvicorn.run(
            fastapi_app,
            host=host,
            port=port,
            log_level=log_level,
            reload=reload,
        )

    @property
    def base_url(self):
        return f"http://truffle-{self.truffle_magic_number}.local"

    def completion(
        self,
        input: str,
        model: str = "meta-llama/Llama-3.2-1b-instruct",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: list = None,
        top_k: int = 40,
        repeat_penalty: float = 1.1,
    ):
        import requests

        response = requests.post(
            f"{self.base_url}/v1/completions",
            json={
                "model": model,
                "prompt": input,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
                "stop": stop,
                "top_k": top_k,
                "repeat_penalty": repeat_penalty,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["text"]

    def embed(
        self,
        input: str,
        model: str = "meta-llama/Llama-3.2-1b",
        encoding_format: str = "float",
        normalize: bool = True,
    ):
        import requests

        response = requests.post(
            f"{self.base_url}/v1/embeddings",
            json={
                "model": model,
                "input": input,
                "encoding_format": encoding_format,
                "normalize": normalize,
            },
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
