from datasage.llm.base import LLMClient


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.model = model
        self._api_key = api_key

    def _client(self):
        try:
            from openai import OpenAI
            return OpenAI(api_key=self._api_key)
        except ImportError:
            raise RuntimeError(
                "OpenAI backend requires: pip install datasage[openai]"
            )

    def complete(self, prompt: str, system: str = "") -> str:
        client = self._client()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(model=self.model, messages=messages)
        return resp.choices[0].message.content

    def is_available(self) -> bool:
        try:
            self._client()
            return bool(self._api_key)
        except RuntimeError:
            return False
