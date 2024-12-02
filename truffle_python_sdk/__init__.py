from pydantic import BaseModel
from functools import wraps
from typing import Literal
import stringcase
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
    
    def start(self, mode: Literal["grpc", "rest"] = "rest"):
        match mode:
            case "grpc":
                self._start_grpc_server()
            case "rest":
                self._start_rest_server()
            case _:
                raise ValueError(f"Invalid mode: {mode}")
            
    def _get_tools(self):
        import inspect
        from pydantic import BaseModel

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '__truffle_tool__'):
                tool_name = attr.__truffle_tool__['name']
                sig = inspect.signature(attr)
                parameters = sig.parameters
                RequestModel = None

                if len(parameters) > 1:  # Exclude 'self'
                    fields = {}
                    for name, param in list(parameters.items())[1:]:
                        annotation = param.annotation if param.annotation != inspect._empty else str
                        fields[name] = (annotation, ...)
                    RequestModel = type(f"{stringcase.capitalize(tool_name)}Request", (BaseModel,), fields)

                yield tool_name, attr, RequestModel

    def _start_grpc_server(self):
        import grpc
        from concurrent import futures
        import os
        from grpc_tools import protoc

        # Step 1: Generate the .proto file
        proto_content = self._generate_proto_file()
        proto_file_path = os.path.join(os.getcwd(), 'truffle.proto')
        with open(proto_file_path, 'w') as f:
            f.write(proto_content)

        # Step 2: Compile the .proto file
        protoc.main((
            '',
            f'-I{os.getcwd()}',
            f'--python_out={os.getcwd()}',
            f'--grpc_python_out={os.getcwd()}',
            proto_file_path,
        ))

        # Step 3: Import the generated modules
        import truffle_pb2
        import truffle_pb2_grpc

        # Step 4: Implement the Servicer
        class TruffleServicer(truffle_pb2_grpc.TruffleServicer):
            def __init__(self, app):
                self.app = app

            # Dynamically define RPC methods for each tool
            def __getattr__(self, name):
                tools = {tool_name: (attr, RequestModel) for tool_name, attr, RequestModel in self.app._get_tools()}
                if name in tools:
                    def method(request, context):
                        attr, RequestModel = tools[name]
                        kwargs = {field.name: getattr(request, field.name) for field in request.DESCRIPTOR.fields}
                        result = attr(self.app, **kwargs)
                        return getattr(truffle_pb2, f'{name}Response')(result=str(result))
                    return method
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        # Create a gRPC server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        truffle_pb2_grpc.add_TruffleServicer_to_server(TruffleServicer(self), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        print("gRPC server is running on port 50051...")
        server.wait_for_termination()

    def _generate_proto_file(self):
        # Generate the .proto file content based on the tools
        lines = [
            'syntax = "proto3";',
            '',
            'package truffle;',
            '',
            'service Truffle {'
        ]

        # Collect tools information
        tools = list(self._get_tools())

        # Define RPC methods in the service
        for tool_name, _, _ in tools:
            lines.append(f'  rpc {tool_name}({tool_name}Request) returns ({tool_name}Response);')

        lines.append('}')

        # Define messages for requests and responses
        for tool_name, _, RequestModel in tools:
            # Request message
            lines.append(f'message {tool_name}Request {{')
            if RequestModel:
                field_number = 1
                for field_name, field_type in RequestModel.__annotations__.items():
                    proto_type = self._python_type_to_proto_type(field_type)
                    lines.append(f'  {proto_type} {field_name} = {field_number};')
                    field_number += 1
            lines.append('}')

            # Response message
            lines.append(f'message {tool_name}Response {{')
            # For simplicity, we'll assume result is a string
            lines.append('  string result = 1;')
            lines.append('}')

        return '\n'.join(lines)

    def _python_type_to_proto_type(self, python_type):
        # Map Python types to protobuf types
        type_map = {
            int: 'int32',
            float: 'float',
            str: 'string',
            bool: 'bool',
        }
        # Handle typing types
        origin = getattr(python_type, '__origin__', None)
        if origin:
            if origin is list:
                item_type = python_type.__args__[0]
                return f'repeated {self._python_type_to_proto_type(item_type)}'
            # Add more cases as needed
        return type_map.get(python_type, 'string')  # Default to string if unknown

    def _start_rest_server(self):
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

        uvicorn.run(app, host="0.0.0.0", port=8000)
    
    @tool()
    def save(self) -> BaseModel:
        return self
    
    @tool()
    def load(self, state: BaseModel):
        self.__dict__.update(state.__dict__)
