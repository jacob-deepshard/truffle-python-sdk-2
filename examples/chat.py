from truffle_sdk import App, tool
from dylans_truffle_sdk import completion, embedding
from typing import List

class ChatApp(App):
    conversation: List[str] = []

    @tool()
    def chat(self, message: str) -> str:
        # Add the user's message to the conversation
        self.conversation.append(f"User: {message}")

        # Generate a response (for simplicity, echoing the message)
        # In a real application, integrate with an AI model here
        response = completion(self.conversation)

        # Add the assistant's response to the conversation
        self.conversation.append(response)

        return response

chat_app = ChatApp()

if __name__ == "__main__":
    import truffle

    truffle.start(chat_app)
