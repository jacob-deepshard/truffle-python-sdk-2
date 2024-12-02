from truffle_python_sdk import TruffleApp, tool, Client


class EchoApp(TruffleApp):

    @tool()
    def echo(self, message: str) -> str:
        return message


app = EchoApp()

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
