from datasage.llm.base import LLMClient


class OllamaClient(LLMClient):
    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3"):
        self.host = host
        self.model = model

    def _client(self):
        try:
            import ollama
            return ollama.Client(host=self.host)
        except ImportError:
            raise RuntimeError(
                "Ollama backend requires: pip install datasage[ollama]"
            )

    def complete(self, prompt: str, system: str = "") -> str:
        client = self._client()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat(model=self.model, messages=messages)
        return resp["message"]["content"]

    def is_available(self) -> bool:
        try:
            import requests
            r = requests.get(f"{self.host}/api/tags", timeout=2)
            return r.status_code == 200
        except Exception:
            return False
