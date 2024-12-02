# Truffle Python SDK

Welcome to the Truffle Python SDK! This SDK allows developers to create applications for the Truffle Computer easily. It provides a framework for building tools that can be exposed via gRPC interfaces, enabling seamless integration and communication.

## Getting Started

This guide will help you set up your development environment and create your first Truffle application.

### Prerequisites

- **Python 3.9 or higher**
- `pip` package manager
- `virtualenv` (optional but recommended)

### Installation

First, clone the repository and navigate to the project directory:

```bash
git clone https://github.com/yourusername/truffle-python-sdk.git
cd truffle-python-sdk
```

*(Replace `yourusername` with the actual username or organization name.)*

(Optional) Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Creating Your First Truffle App

To create a Truffle app, you need to define a class inheriting from `TruffleApp` and decorate your methods with `@tool()`. Here's a simple example:

```python
from truffle_python_sdk import TruffleApp, tool

class EchoApp(TruffleApp):

    @tool()
    def echo(self, message: str) -> str:
        return message

app = EchoApp()

if __name__ == "__main__":
    app.start(mode="grpc")
```

In this example, we create an `EchoApp` that has one tool method `echo`, which simply returns the message it receives.

### Running Your App

To run your app, use the following command:

```bash
python your_app.py
```

Replace `your_app.py` with the name of your script file. The app will start a gRPC server listening for incoming requests from the truffle computer.

## Defining Tools

Tools are methods of your `TruffleApp` subclass decorated with `@tool()`. Each tool can accept parameters and should return a result.

### Example: Calculator App

```python
from truffle_python_sdk import TruffleApp, tool

class CalculatorApp(TruffleApp):

    @tool()
    def add(self, a: float, b: float) -> float:
        return a + b

    @tool()
    def subtract(self, a: float, b: float) -> float:
        return a - b

app = CalculatorApp()

if __name__ == "__main__":
    app.start(mode="grpc")
```

This `CalculatorApp` provides basic arithmetic operations that can be accessed over gRPC.

## State Management

Your app can maintain state by defining class attributes. These can be primitive types, lists, dictionaries, or even custom objects.

### Example: Chat App

```python
from truffle_python_sdk import TruffleApp, tool
from typing import List

class ChatApp(TruffleApp):
    conversation: List[str] = []

    @tool()
    def chat(self, message: str) -> str:
        # Add the user's message to the conversation
        self.conversation.append(f"User: {message}")
        
        # Generate a response (for simplicity, echoing the message)
        response = f"Echo: {message}"
        
        # Add the assistant's response to the conversation
        self.conversation.append(f"Assistant: {response}")
        
        return response

app = ChatApp()

if __name__ == "__main__":
    app.start(mode="grpc")
```

The `ChatApp` maintains a conversation history and generates responses based on user input.

## Advanced Example: Retrieval-Augmented Generation (RAG) Chat App

```python
from truffle_python_sdk import TruffleApp, tool
from your_embedding_module import embedding  # Replace with your embedding function
import numpy as np
from typing import List, Dict

class RAGChatApp(TruffleApp):
    """
    A Retrieval-Augmented Generation Chat Application.
    """
    conversation: List[Dict[str, str]] = []
    knowledge_base: List[Dict[str, np.ndarray]] = []

    @tool()
    def add_knowledge(self, text: str) -> str:
        """
        Add text to the knowledge base via an API endpoint.
        """
        self.add_to_knowledge_base(text)
        return f"Added to knowledge base: {text}"

    @tool()
    def chat(self, message: str) -> str:
        """
        Chat method to handle user messages and generate responses.
        """
        # Add the user's message to the conversation
        self.conversation.append({"role": "user", "message": message})

        # Retrieve relevant documents
        relevant_docs = self.retrieve_relevant_docs(message)

        # Generate a response (for simplicity, echoing the message)
        response = self.generate_response(message, relevant_docs)

        # Add the assistant's response to the conversation
        self.conversation.append({"role": "assistant", "message": response})

        return response

    def add_to_knowledge_base(self, text: str):
        """
        Add text to the knowledge base along with its embedding.
        """
        embedding_vector = np.array(embedding(text))
        self.knowledge_base.append({
            'text': text,
            'embedding': embedding_vector
        })

    def retrieve_relevant_docs(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve the most relevant documents from the knowledge base for the given query.
        """
        query_embedding = np.array(embedding(query))
        similarities = []
        for doc in self.knowledge_base:
            similarity = np.dot(query_embedding, doc['embedding'])
            similarities.append((similarity, doc['text']))
        similarities.sort(reverse=True)
        relevant_texts = [text for _, text in similarities[:top_k]]
        return relevant_texts

    def generate_response(self, message: str, relevant_docs: List[str]) -> str:
        """
        Generate a response using the retrieved documents.
        """
        # Implement your response generation logic here
        return "This is a placeholder response."

app = RAGChatApp()

if __name__ == "__main__":
    app.start(mode="grpc")
```

This advanced app demonstrates how to incorporate a knowledge base and retrieval mechanisms into your Truffle app.

## Command-Line Interface

You can also run your app using the Truffle CLI:

```bash
python -m truffle-python-sdk run:grpc your_app
```

This command starts your app in gRPC mode.

### Generating the `.proto` File

To generate the `.proto` file without starting a server, use:

```bash
python -m truffle-python-sdk proto your_app
```

## Testing Your App

You can test your gRPC server using tools like `grpcurl` or by writing a client in the language of your choice using the generated `.proto` file.

### Example using `grpcurl`:

```bash
grpcurl -plaintext -d '{"message": "Hello"}' localhost:50051 truffle.Truffle/echo
```

Replace `truffle.Truffle/echo` with the appropriate service and method names from your `.proto` file.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License.
