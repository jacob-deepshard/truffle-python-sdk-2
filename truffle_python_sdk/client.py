from truffle_python_sdk.app import TruffleApp


class Client:
    truffle_magic_number = 18008
    
    def run(self, app: TruffleApp, *args, **kwargs):
        app.run(*args, **kwargs)
    
    @property
    def base_url(self):
        return f"http://truffle-{self.truffle_magic_number}.local"
    
    def completion(
        self,
        input: str,
        model: str = "meta-llama/Llama-3.2-1b-instruct",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: list = None,
        top_k: int = 40,
        repeat_penalty: float = 1.1,
    ):
        import requests
        response = requests.post(
            "http://localhost:8080/v1/completions",
            json={
                "model": model,
                "prompt": input,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
                "stop": stop,
                "top_k": top_k,
                "repeat_penalty": repeat_penalty
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["text"]

    def embed(
        self,
        input: str, 
        model: str = "meta-llama/Llama-3.2-1b",
        encoding_format: str = "float",
        normalize: bool = True
    ):
        import requests
        response = requests.post(
            f"{self.base_url}/v1/embeddings",
            json={
                "model": model,
                "input": input,
                "encoding_format": encoding_format,
                "normalize": normalize
            }
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]