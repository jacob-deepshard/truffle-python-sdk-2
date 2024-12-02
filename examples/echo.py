from truffle_sdk import App, tool

class EchoApp(App):

    @tool()
    def echo(self, message: str) -> str:
        return message

echo_app = EchoApp()
echo_app.start()