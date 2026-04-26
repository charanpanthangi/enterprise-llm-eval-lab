from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ModelResponse:
    content: str
    input_tokens: int = 0
    output_tokens: int = 0
    raw: dict | None = None


class BaseModelClient(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def generate(self, prompt: str, messages: list[dict] | None = None) -> ModelResponse:
        raise NotImplementedError
