import grpc
from concurrent import futures
import os
from grpc_tools import protoc
import inspect
from pydantic import BaseModel
from typing import get_origin, get_args, List, Dict, Union


def generate_proto_file(tools):
    """
    Generate the .proto file content based on the tools provided.
    """
    lines = ['syntax = "proto3";', "", "package truffle;", "", "service Truffle {"]

    # Define RPC methods in the service
    for tool in tools:
        tool_name = tool["name"]
        lines.append(
            f"  rpc {tool_name}({tool_name}Request) returns ({tool_name}Response);"
        )

    lines.append("}")

    # Collect message definitions to handle duplicates
    message_definitions = {}

    # Define messages for requests and responses
    for tool in tools:
        tool_name = tool["name"]

        # Request message
        request_fields = []
        field_number = 1
        for param in tool.get("parameters", []):
            param_name = param["name"]
            param_type = param["annotation"]
            proto_type = python_type_to_proto_type(param_type, message_definitions)
            request_fields.append(f"  {proto_type} {param_name} = {field_number};")
            field_number += 1
        request_message = (
            f"message {tool_name}Request {{\n" + "\n".join(request_fields) + "\n}}"
        )
        message_definitions[f"{tool_name}Request"] = request_message

        # Response message
        return_type = tool.get("return_type", None)
        # Handle complex return types if needed
        if return_type is inspect.Signature.empty:
            response_fields = ["  string result = 1;"]
        else:
            proto_type = python_type_to_proto_type(return_type, message_definitions)
            response_fields = [f"  {proto_type} result = 1;"]
        response_message = (
            f"message {tool_name}Response {{\n" + "\n".join(response_fields) + "\n}}"
        )
        message_definitions[f"{tool_name}Response"] = response_message

    # Append all message definitions
    for message in message_definitions.values():
        lines.append("")
        lines.append(message)

    proto_content = "\n".join(lines)

    # Write the proto content to a file
    proto_file_path = "truffle.proto"
    with open(proto_file_path, "w") as f:
        f.write(proto_content)
    print(f"Generated {proto_file_path}")


def python_type_to_proto_type(python_type, message_definitions):
    """
    Map Python types to protobuf types.
    """
    # Base type mapping
    type_map = {
        int: "int32",
        float: "float",
        str: "string",
        bool: "bool",
        bytes: "bytes",
    }

    # Handle typing types
    origin = get_origin(python_type)
    args = get_args(python_type)

    if origin is list or origin is List:
        item_type = args[0] if args else str
        return f"repeated {python_type_to_proto_type(item_type, message_definitions)}"
    elif origin is dict or origin is Dict:
        # Protobuf maps must have scalar types for keys
        key_type = (
            python_type_to_proto_type(args[0], message_definitions)
            if args
            else "string"
        )
        value_type = (
            python_type_to_proto_type(args[1], message_definitions)
            if args
            else "string"
        )
        return f"map<{key_type}, {value_type}>"
    elif origin is Union:
        # For Unions, pick the first type (excluding NoneType)
        non_none_types = [t for t in args if t is not type(None)]
        if non_none_types:
            return python_type_to_proto_type(non_none_types[0], message_definitions)
        else:
            return "string"  # Default to string if only NoneType is present
    elif origin is None:
        return type_map.get(python_type, "string")  # Handle simple types
    elif issubclass(python_type, BaseModel):
        # Generate message for the Pydantic model
        model_name = python_type.__name__
        if model_name not in message_definitions:
            fields = []
            field_number = 1
            for name, field in python_type.__fields__.items():
                field_type = python_type_to_proto_type(field.type_, message_definitions)
                fields.append(f"  {field_type} {name} = {field_number};")
                field_number += 1
            message = f"message {model_name} {{\n" + "\n".join(fields) + "\n}}"
            message_definitions[model_name] = message
        return model_name
    else:
        # For custom types or complex structures, default to 'string' or define a message
        return "string"  # Adjust as needed for complex types

    # Default to 'string' if type is not recognized
    return "string"


def start_grpc_server(
    tools, app_instance, host="0.0.0.0", port=50051, log_level="info"
):
    """
    Start the gRPC server using the provided tools.
    """
    # Step 1: Generate the .proto file
    generate_proto_file(tools)

    # Step 2: Compile the .proto file
    proto_file_path = os.path.join(os.getcwd(), "truffle.proto")
    protoc.main(
        (
            "",
            f"-I{os.getcwd()}",
            f"--python_out={os.getcwd()}",
            f"--grpc_python_out={os.getcwd()}",
            proto_file_path,
        )
    )

    # Step 3: Import the generated modules
    import truffle_pb2
    import truffle_pb2_grpc

    # Step 4: Implement the Servicer
    class TruffleServicer(truffle_pb2_grpc.TruffleServicer):
        def __init__(self, app_instance, tools):
            self.app_instance = app_instance
            self.tools = {tool["name"]: tool for tool in tools}

    # Step 5: Dynamically add RPC methods to the Servicer class
    for tool_name, tool in ((tool["name"], tool) for tool in tools):
        request_class = getattr(truffle_pb2, f"{tool_name}Request")
        response_class = getattr(truffle_pb2, f"{tool_name}Response")
        func = tool["function"]

        def create_rpc_method(func, request_class, response_class):
            # Define the RPC method
            def rpc_method(self, request, context):
                kwargs = {}
                # Extract request parameters
                for field in request.DESCRIPTOR.fields:
                    kwargs[field.name] = getattr(request, field.name)
                # Call the tool function
                result = func(self.app_instance, **kwargs)
                # Simplify result if necessary
                result = standardize(result)
                # Build the response
                if isinstance(result, dict):
                    return response_class(**result)
                else:
                    return response_class(result=result)

            return rpc_method

        # Add the method to TruffleServicer
        rpc_method = create_rpc_method(func, request_class, response_class)
        rpc_method_name = tool_name  # Must match the name defined in .proto
        setattr(TruffleServicer, rpc_method_name, rpc_method)

    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    truffle_pb2_grpc.add_TruffleServicer_to_server(
        TruffleServicer(app_instance, tools), server
    )
    server.add_insecure_port(f"{host}:{port}")
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
    if hasattr(object, "__dataclass_fields__"):
        return {
            field: standardize(getattr(object, field))
            for field in object.__dataclass_fields__
        }

    # Handle Pydantic models
    if hasattr(object, "dict"):
        try:
            return standardize(object.dict())
        except:
            pass

    # Handle objects with __dict__ attribute
    if hasattr(object, "__dict__"):
        return standardize(object.__dict__)

    # Default fallback - convert to string
    return str(object)
