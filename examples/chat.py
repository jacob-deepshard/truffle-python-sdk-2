from truffle_python_sdk import TruffleApp, tool
from dylans_truffle_sdk import completion
from typing import List

class ChatApp(TruffleApp):
    conversation: List[str] = []

    @tool()
    def chat(self, message: str) -> str:
        # Add the user's message to the conversation
        self.conversation.append(f"User: {message}")

        # Generate a response (for simplicity, echoing the message)
        # In a real application, integrate with an AI model here
        response = completion(self.conversation)

        # Add the assistant's response to the conversation
        self.conversation.append(f"Assistant: {response}")

        return response

app = ChatApp()

if __name__ == "__main__":
    app.start()
