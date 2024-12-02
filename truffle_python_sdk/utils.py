import grpc
from concurrent import futures
import os
from grpc_tools import protoc
import inspect
from pydantic import BaseModel
import stringcase
from typing import get_origin, get_args, List, Dict, Union

def generate_proto_file(tools):
    """
    Generate the .proto file content based on the tools provided.
    """
    lines = [
        'syntax = "proto3";',
        '',
        'package truffle;',
        '',
        'service Truffle {'
    ]

    # Define RPC methods in the service
    for tool in tools:
        tool_name = tool['name']
        lines.append(f'  rpc {tool_name}({tool_name}Request) returns ({tool_name}Response);')

    lines.append('}')

    # Define messages for requests and responses
    for tool in tools:
        tool_name = tool['name']

        # Request message
        lines.append(f'message {tool_name}Request {{')
        field_number = 1
        for param in tool.get('parameters', []):
            param_name = param['name']
            param_type = param['annotation']
            proto_type = python_type_to_proto_type(param_type)
            lines.append(f'  {proto_type} {param_name} = {field_number};')
            field_number += 1
        lines.append('}')

        # Response message
        lines.append(f'message {tool_name}Response {{')
        return_type = tool.get('return_type', None)
        if return_type is inspect.Signature.empty:
            # Default to string if no return type annotation
            lines.append('  string result = 1;')
        else:
            proto_type = python_type_to_proto_type(return_type)
            lines.append(f'  {proto_type} result = 1;')
        lines.append('}')

    proto_content = '\n'.join(lines)

    # Write the proto content to a file
    proto_file_path = 'truffle.proto'
    with open(proto_file_path, 'w') as f:
        f.write(proto_content)
    print(f"Generated {proto_file_path}")

def python_type_to_proto_type(python_type):
    """
    Map Python types to protobuf types.
    """
    # Map Python types to protobuf types
    type_map = {
        int: 'int32',
        float: 'float',
        str: 'string',
        bool: 'bool',
        bytes: 'bytes',
    }

    # Handle typing types
    origin = get_origin(python_type)
    args = get_args(python_type)

    if origin is list or origin is List:
        item_type = args[0] if args else str
        return f'repeated {python_type_to_proto_type(item_type)}'
    elif origin is dict or origin is Dict:
        # Protobuf supports maps
        key_type = python_type_to_proto_type(args[0]) if args else 'string'
        value_type = python_type_to_proto_type(args[1]) if args else 'string'
        return f'map<{key_type}, {value_type}>'
    elif origin is Union:
        # For Unions, pick the first type (excluding NoneType)
        non_none_types = [t for t in args if t is not type(None)]
        if non_none_types:
            return python_type_to_proto_type(non_none_types[0])
        else:
            return 'string'  # Default to string if only NoneType is present
    elif origin is None:
        return type_map.get(python_type, 'string')  # Handle simple types
    else:
        # For custom types, default to string or raise an error
        return 'string'  # Adjust as needed

    return type_map.get(python_type, 'string')  # Default to string if unknown

def start_grpc_server(tools, app_instance, host="0.0.0.0", port=50051, log_level="info"):
    """
    Start the gRPC server using the provided tools.
    """
    # Step 1: Generate the .proto file
    generate_proto_file(tools)

    # Step 2: Compile the .proto file
    proto_file_path = os.path.join(os.getcwd(), 'truffle.proto')
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
        def __init__(self, app_instance, tools):
            self.app_instance = app_instance
            self.tools = {tool['name']: tool for tool in tools}

        # Dynamically define RPC methods for each tool
        def __getattr__(self, name):
            if name in self.tools:
                def method(request, context):
                    tool = self.tools[name]
                    func = tool['function']
                    kwargs = {}
                    # Extract request parameters
                    for field in request.DESCRIPTOR.fields:
                        kwargs[field.name] = getattr(request, field.name)
                    # Call the tool function
                    result = func(self.app_instance, **kwargs)
                    # Build the response
                    response_class = getattr(truffle_pb2, f'{name}Response')
                    
                    # Simplify result if necessary
                    result = standardize(result)
                    
                    # Check if result is of a basic type or a complex object
                    if isinstance(result, (str, int, float, bool)):
                        return response_class(result=result)
                    elif isinstance(result, dict):
                        # Set fields of the response message
                        response = response_class(**result)
                        return response
                    else:
                        # Handle serialization for custom objects
                        response = response_class()
                        for attr_name in dir(result):
                            if not attr_name.startswith('_'):
                                attr_value = getattr(result, attr_name)
                                setattr(response, attr_name, attr_value)
                        return response
                return method
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    truffle_pb2_grpc.add_TruffleServicer_to_server(TruffleServicer(app_instance, tools), server)
    server.add_insecure_port(f'{host}:{port}')
    server.start()
    print(f"gRPC server is running on {host}:{port}...")
    server.wait_for_termination()

def standardize(object):
    """Convert complex data structures into primitive Python types.
    
    Args:
        object: Any Python object to convert
        
    Returns:
        A simplified version using only primitive types (str, int, float, bool),
        lists, dictionaries and sets
    """
    # Handle None
    if object is None:
        return None
        
    # Handle primitive types
    if isinstance(object, (str, int, float, bool)):
        return object
        
    # Handle lists, tuples and other sequences
    if isinstance(object, (list, tuple, set)):
        return [standardize(item) for item in object]
        
    # Handle dictionaries
    if isinstance(object, dict):
        return {str(k): standardize(v) for k, v in object.items()}
        
    # Handle dataclasses
    if hasattr(object, '__dataclass_fields__'):
        return {
            field: standardize(getattr(object, field)) 
            for field in object.__dataclass_fields__
        }
        
    # Handle Pydantic models
    if hasattr(object, 'dict'):
        try:
            return standardize(object.dict())
        except:
            pass
            
    # Handle objects with __dict__ attribute
    if hasattr(object, '__dict__'):
        return standardize(object.__dict__)
        
    # Default fallback - convert to string
    return str(object)