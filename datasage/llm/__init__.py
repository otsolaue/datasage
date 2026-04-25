from datasage.config import Config
from datasage.llm.base import LLMClient


def get_client(cfg: Config) -> LLMClient:
    """Return the appropriate LLMClient for the configured backend."""
    if cfg.backend == "anthropic":
        from datasage.llm.anthropic import AnthropicClient
        return AnthropicClient(api_key=cfg.api_key, model=cfg.model)
    elif cfg.backend == "openai":
        from datasage.llm.openai import OpenAIClient
        return OpenAIClient(api_key=cfg.api_key, model=cfg.model)
    elif cfg.backend == "ollama":
        from datasage.llm.ollama import OllamaClient
        return OllamaClient(host=cfg.ollama_host, model=cfg.model)
    raise ValueError(f"Unknown backend: {cfg.backend}")
