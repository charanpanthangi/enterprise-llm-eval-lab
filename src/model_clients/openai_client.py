import os

from openai import OpenAI

from src.model_clients.base import BaseModelClient, ModelResponse


class OpenAIModelClient(BaseModelClient):
    def __init__(self, config: dict):
        super().__init__(config)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(self, prompt: str, messages: list[dict] | None = None) -> ModelResponse:
        payload_messages = messages or [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=self.config["model_name"],
            messages=payload_messages,
            temperature=self.config.get("temperature", 0.2),
            max_tokens=self.config.get("max_tokens", 1000),
            timeout=self.config.get("timeout", 60),
        )
        usage = response.usage
        return ModelResponse(
            content=response.choices[0].message.content or "",
            input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            output_tokens=getattr(usage, "completion_tokens", 0) or 0,
            raw=response.model_dump(),
        )
