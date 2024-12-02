import sys
import os
import threading
import time
import requests
import grpc

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test functions for direct Python method calls


def test_echo_app_python():
    from examples.echo import app as echo_app

    # Directly call the echo method
    message = "Hello, Truffle!"
    result = echo_app.echo(message=message)
    assert result == "Hello, Truffle!"


def test_calculator_app_python():
    from examples.calculator import app as calculator_app

    # Test addition
    result = calculator_app.add(a=2, b=3)
    assert result == 5

    # Test subtraction
    result = calculator_app.subtract(a=5, b=2)
    assert result == 3

    # Test multiplication
    result = calculator_app.multiply(a=3, b=4)
    assert result == 12

    # Test division
    result = calculator_app.divide(a=10, b=2)
    assert result == 5

    # Test division by zero
    result = calculator_app.divide(a=5, b=0)
    assert result == "Error: Cannot divide by zero."


def test_chat_app_python():
    from examples.chat import app as chat_app

    # Directly call the chat method
    message = "Hello!"
    result = chat_app.chat(message=message)
    assert isinstance(result, str)
    assert len(result) > 0


def test_rag_chat_app_python():
    from examples.rag_chat import app as rag_chat_app

    # Add knowledge to the knowledge base
    rag_chat_app.add_knowledge(text="The capital of France is Paris.")

    # Ask a question related to the knowledge
    result = rag_chat_app.chat(message="What is the capital of France?")
    assert "Paris" in result


# Helper functions


def run_app_in_background(app_instance, mode, host, port):
    # Start the app in a separate thread
    def start():
        app_instance.start(mode=mode, host=host, port=port)

    thread = threading.Thread(target=start)
    thread.daemon = True
    thread.start()
    # Give the server a moment to start up
    time.sleep(1)
    return thread


# Test functions for REST mode


def test_echo_app_rest():
    from examples.echo import app as echo_app

    host = "127.0.0.1"
    port = 8000

    # Start the app in REST mode
    run_app_in_background(echo_app, mode="rest", host=host, port=port)

    # Send a POST request to the echo endpoint
    url = f"http://{host}:{port}/echo"
    data = {"message": "Hello, Truffle!"}
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()["result"]
    assert result == "Hello, Truffle!"


def test_calculator_app_rest():
    from examples.calculator import app as calculator_app

    host = "127.0.0.1"
    port = 8001

    # Start the app in REST mode
    run_app_in_background(calculator_app, mode="rest", host=host, port=port)

    # Test addition
    url = f"http://{host}:{port}/add"
    data = {"a": 2, "b": 3}
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()["result"]
    assert result == 5

    # Test subtraction
    url = f"http://{host}:{port}/subtract"
    data = {"a": 5, "b": 2}
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()["result"]
    assert result == 3

    # Test multiplication
    url = f"http://{host}:{port}/multiply"
    data = {"a": 3, "b": 4}
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()["result"]
    assert result == 12

    # Test division
    url = f"http://{host}:{port}/divide"
    data = {"a": 10, "b": 2}
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()["result"]
    assert result == 5

    # Test division by zero
    url = f"http://{host}:{port}/divide"
    data = {"a": 5, "b": 0}
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()["result"]
    assert result == "Error: Cannot divide by zero."


def test_chat_app_rest():
    from examples.chat import app as chat_app

    host = "127.0.0.1"
    port = 8002

    # Start the app in REST mode
    run_app_in_background(chat_app, mode="rest", host=host, port=port)

    # Send a POST request to the chat endpoint
    url = f"http://{host}:{port}/chat"
    data = {"message": "Hello!"}
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()["result"]
    assert isinstance(result, str)
    assert len(result) > 0


def test_rag_chat_app_rest():
    from examples.rag_chat import app as rag_chat_app

    host = "127.0.0.1"
    port = 8003

    # Start the app in REST mode
    run_app_in_background(rag_chat_app, mode="rest", host=host, port=port)

    # Add knowledge to the knowledge base
    url = f"http://{host}:{port}/add_knowledge"
    data = {"text": "The capital of France is Paris."}
    response = requests.post(url, json=data)
    assert response.status_code == 200

    # Ask a question related to the knowledge
    url = f"http://{host}:{port}/chat"
    data = {"message": "What is the capital of France?"}
    response = requests.post(url, json=data)
    assert response.status_code == 200
    result = response.json()["result"]
    assert "Paris" in result


# Test functions for gRPC mode


def test_echo_app_grpc():
    from examples.echo import app as echo_app

    host = "127.0.0.1"
    port = 50051

    # Start the app in gRPC mode
    run_app_in_background(echo_app, mode="grpc", host=host, port=port)

    # Import the generated gRPC modules
    import truffle_pb2
    import truffle_pb2_grpc

    # Create a gRPC channel and stub
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = truffle_pb2_grpc.TruffleStub(channel)

    # Call the echo RPC method
    request = truffle_pb2.echoRequest(message="Hello, Truffle!")
    response = stub.echo(request)
    result = response.result
    assert result == "Hello, Truffle!"


def test_calculator_app_grpc():
    from examples.calculator import app as calculator_app

    host = "127.0.0.1"
    port = 50052

    # Start the app in gRPC mode
    run_app_in_background(calculator_app, mode="grpc", host=host, port=port)

    # Import the generated gRPC modules
    import truffle_pb2
    import truffle_pb2_grpc

    # Create a gRPC channel and stub
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = truffle_pb2_grpc.TruffleStub(channel)

    # Test addition
    request = truffle_pb2.addRequest(a=2, b=3)
    response = stub.add(request)
    result = response.result
    assert result == 5

    # Test subtraction
    request = truffle_pb2.subtractRequest(a=5, b=2)
    response = stub.subtract(request)
    result = response.result
    assert result == 3

    # Test multiplication
    request = truffle_pb2.multiplyRequest(a=3, b=4)
    response = stub.multiply(request)
    result = response.result
    assert result == 12

    # Test division
    request = truffle_pb2.divideRequest(a=10, b=2)
    response = stub.divide(request)
    result = response.result
    assert result == 5

    # Test division by zero
    request = truffle_pb2.divideRequest(a=5, b=0)
    response = stub.divide(request)
    result = response.result
    assert result == "Error: Cannot divide by zero."


def test_chat_app_grpc():
    from examples.chat import app as chat_app

    host = "127.0.0.1"
    port = 50053

    # Start the app in gRPC mode
    run_app_in_background(chat_app, mode="grpc", host=host, port=port)

    # Import the generated gRPC modules
    import truffle_pb2
    import truffle_pb2_grpc

    # Create a gRPC channel and stub
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = truffle_pb2_grpc.TruffleStub(channel)

    # Call the chat RPC method
    request = truffle_pb2.chatRequest(message="Hello!")
    response = stub.chat(request)
    result = response.result
    assert isinstance(result, str)
    assert len(result) > 0


def test_rag_chat_app_grpc():
    from examples.rag_chat import app as rag_chat_app

    host = "127.0.0.1"
    port = 50054

    # Start the app in gRPC mode
    run_app_in_background(rag_chat_app, mode="grpc", host=host, port=port)

    # Import the generated gRPC modules
    import truffle_pb2
    import truffle_pb2_grpc

    # Create a gRPC channel and stub
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = truffle_pb2_grpc.TruffleStub(channel)

    # Add knowledge to the knowledge base
    request = truffle_pb2.add_knowledgeRequest(text="The capital of France is Paris.")
    response = stub.add_knowledge(request)

    # Ask a question related to the knowledge
    request = truffle_pb2.chatRequest(message="What is the capital of France?")
    response = stub.chat(request)
    result = response.result
    assert "Paris" in result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run Truffle app tests")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument(
        "--python", action="store_true", help="Run Python direct call tests only"
    )
    parser.add_argument("--rest", action="store_true", help="Run REST API tests only")
    parser.add_argument("--grpc", action="store_true", help="Run gRPC tests only")

    args = parser.parse_args()

    # If no flags specified, run all tests
    if not (args.python or args.rest or args.grpc):
        args.all = True

    test_functions = []

    if args.all or args.python:
        test_functions.extend(
            [
                test_echo_app_python,
                test_calculator_app_python,
                test_chat_app_python,
                test_rag_chat_app_python,
            ]
        )

    if args.all or args.rest:
        test_functions.extend(
            [
                test_echo_app_rest,
                test_calculator_app_rest,
                test_chat_app_rest,
                test_rag_chat_app_rest,
            ]
        )

    if args.all or args.grpc:
        test_functions.extend(
            [
                test_echo_app_grpc,
                test_calculator_app_grpc,
                test_chat_app_grpc,
                test_rag_chat_app_grpc,
            ]
        )

    # Run selected tests
    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
        except Exception as e:
            print(f"✗ {test_func.__name__}")
            print(f"  Error: {str(e)}")


if __name__ == "__main__":
    main()
