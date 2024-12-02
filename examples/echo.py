from truffle_python_sdk import TruffleApp, utils

class EchoApp(TruffleApp):

    @utils()
    def echo(self, message: str) -> str:
        return message

app = EchoApp()

if __name__ == "__main__":
    app.start()
