from functools import wraps
from typing import Literal

import stringcase
from pydantic import BaseModel

from truffle_python_sdk.utils import start_grpc_server, generate_proto_file


def tool(name: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        
        tool_args = {
            "name": name or func.__name__
        }
        
        wrapper.__truffle_tool__ = tool_args
        
        return wrapper
    return decorator

class TruffleApp(BaseModel):
    
    def start(
        self,
        mode: Literal["grpc", "rest"] = "rest",
        host: str = "0.0.0.0",
        port: int = None,
        log_level: str = "info",
        reload: bool = False,
    ):
        if mode == "grpc":
            if port is None:
                port = 50051  # Default gRPC port
            self._start_grpc_server(host, port, log_level)
        elif mode == "rest":
            if port is None:
                port = 8000  # Default REST port
            self._start_rest_server(host, port, log_level, reload)
        else:
            raise ValueError(f"Invalid mode: {mode}")
            
    def _get_tools(self):
        import inspect
        from pydantic import BaseModel

        tools = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '__truffle_tool__'):
                tool_name = attr.__truffle_tool__['name']
                sig = inspect.signature(attr)
                parameters = list(sig.parameters.values())[1:]  # Exclude 'self'
                return_type = sig.return_annotation

                # Collect parameter info
                param_list = []
                fields = {}
                for param in parameters:
                    param_annotation = param.annotation if param.annotation != inspect.Parameter.empty else str
                    param_list.append({
                        'name': param.name,
                        'annotation': param_annotation,
                    })
                    fields[param.name] = (param_annotation, ...)
                
                # Create RequestModel if necessary
                RequestModel = None
                if fields:
                    RequestModel = type(f"{stringcase.capitalize(tool_name)}Request", (BaseModel,), fields)

                tools.append({
                    'name': tool_name,
                    'function': attr,
                    'parameters': param_list,
                    'return_type': return_type,
                    'request_model': RequestModel,
                })

        return tools

    def _start_grpc_server(self, host: str, port: int, log_level: str):
        from .utils import start_grpc_server
        # Extract tools
        tools = self._get_tools()
        start_grpc_server(tools, self, host, port, log_level)

    def generate_proto_files(self):
        from .utils import generate_proto_file
        # Extract tools
        tools = self._get_tools()
        generate_proto_file(tools)

    def _start_rest_server(
        self,
        host: str,
        port: int,
        log_level: str,
        reload: bool,
    ):
        import uvicorn
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        from typing import Callable

        app = FastAPI()

        # Register tool endpoints
        for tool_name, attr, RequestModel in self._get_tools():
            def create_endpoint(func: Callable, request_model):
                async def endpoint(request_data: request_model = None):
                    kwargs = request_data.dict() if request_data else {}
                    result = func(self, **kwargs)
                    return JSONResponse(content={"result": result})
                return endpoint

            endpoint_func = create_endpoint(attr, RequestModel)
            app.post(f"/{tool_name}")(endpoint_func)

        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=log_level,
            reload=reload,
        )
    
    @tool()
    def save(self) -> BaseModel:
        return self
    
    @tool()
    def load(self, state: BaseModel):
        self.__dict__.update(state.__dict__)
