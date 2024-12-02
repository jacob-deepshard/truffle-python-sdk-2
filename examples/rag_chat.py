from truffle_python_sdk import TruffleApp, tool, Client
from typing import List, Dict
import numpy as np  # For local computations


class ChatApp(TruffleApp):
    """
    A Retrieval-Augmented Generation Chat Application.
    """

    conversation: List[Dict[str, str]] = []
    knowledge_base: List[Dict[str, List[float]]] = []  # Use List[float] instead of np.ndarray

    def add_to_knowledge_base(self, text: str):
        """
        Add text to the knowledge base along with its embedding.
        """
        # Get embedding for the text using client's embed method
        embedding_vector = self._client.embed(text)  # Should return a List[float]
        # Store the text and its embedding
        self.knowledge_base.append({"text": text, "embedding": embedding_vector})

    def retrieve_relevant_docs(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve the most relevant documents from the knowledge base for the given query.
        """
        query_embedding = self._client.embed(query)  # Get embedding as List[float]
        query_embedding_np = np.array(query_embedding)  # Convert to numpy array locally
        similarities = []
        for doc in self.knowledge_base:
            doc_embedding_np = np.array(doc["embedding"])  # Convert to numpy array locally
            # Compute cosine similarity
            similarity = np.dot(query_embedding_np, doc_embedding_np) / (
                np.linalg.norm(query_embedding_np) * np.linalg.norm(doc_embedding_np)
            )
            similarities.append((similarity, doc["text"]))
        # Sort the documents by similarity in descending order
        similarities.sort(reverse=True)
        # Return the top_k most similar documents
        relevant_texts = [text for _, text in similarities[:top_k]]
        return relevant_texts

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

        # Construct the prompt for the completion function
        prompt = ""
        for turn in self.conversation:
            prompt += f"{turn['role'].capitalize()}: {turn['message']}\n"
        # Add the retrieved documents to the prompt
        prompt += "\nRelevant Information:\n"
        for doc in relevant_docs:
            prompt += f"- {doc}\n"
        prompt += "\nAssistant:"

        # Generate a response using the client's completion method
        response_text = self._client.completion(prompt)

        # Add the assistant's response to the conversation
        self.conversation.append({"role": "assistant", "message": response_text})

        return response_text


app = ChatApp()

if __name__ == "__main__":
    # Start the app using the Client
    client = Client()
    client.start(
        app=app,
        mode="rest",  # Can be 'rest' or 'grpc'
        host="0.0.0.0",
        port=8000,  # Or any preferred port
        log_level="info",
        reload=False,
    )
