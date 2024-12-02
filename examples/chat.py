from truffle_python_sdk import TruffleApp, tool, Client
from typing import List


class ChatApp(TruffleApp):
    conversation: List[str] = []
    client: Client = Client()

    @tool()
    def chat(self, message: str) -> str:
        # Add the user's message to the conversation
        self.conversation.append(f"User: {message}")

        # Construct the prompt
        prompt = "\n".join(self.conversation) + "\nAssistant:"

        # Generate a response using the client's completion method
        response_text = self.client.completion(prompt)

        # Add the assistant's response to the conversation
        self.conversation.append(f"Assistant: {response_text}")

        return response_text


app = ChatApp()

if __name__ == "__main__":
    client = Client()
    client.start(
        app=app,
        mode="rest",  # Can be 'rest' or 'grpc'
        host="0.0.0.0",
        port=8000,  # Or any preferred port
        log_level="info",
        reload=False,
    )
