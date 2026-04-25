from datasage.llm.base import LLMClient


class AnthropicClient(LLMClient):
    def __init__(self, api_key: str, model: str = "claude-opus-4-6"):
        self.model = model
        self._api_key = api_key

    def _client(self):
        try:
            import anthropic
            return anthropic.Anthropic(api_key=self._api_key)
        except ImportError:
            raise RuntimeError(
                "Anthropic backend requires: pip install datasage[anthropic]"
            )

    def complete(self, prompt: str, system: str = "") -> str:
        client = self._client()
        kwargs = {"model": self.model, "max_tokens": 4096, "messages": [{"role": "user", "content": prompt}]}
        if system:
            kwargs["system"] = system
        msg = client.messages.create(**kwargs)
        return msg.content[0].text

    def is_available(self) -> bool:
        try:
            self._client()
            return bool(self._api_key)
        except RuntimeError:
            return False
