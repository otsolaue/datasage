from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Common interface for all LLM backends."""

    @abstractmethod
    def complete(self, prompt: str, system: str = "") -> str:
        """Send a prompt and return the text response."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the backend is reachable / credentials are set."""
        ...
