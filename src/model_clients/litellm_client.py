from litellm import completion

from src.model_clients.base import BaseModelClient, ModelResponse


class LiteLLMClient(BaseModelClient):
    def generate(self, prompt: str, messages: list[dict] | None = None) -> ModelResponse:
        payload_messages = messages or [{"role": "user", "content": prompt}]
        response = completion(
            model=self.config["model_name"],
            messages=payload_messages,
            temperature=self.config.get("temperature", 0.2),
            max_tokens=self.config.get("max_tokens", 1000),
            timeout=self.config.get("timeout", 60),
        )
        usage = response.get("usage", {})
        content = response["choices"][0]["message"]["content"]
        return ModelResponse(
            content=content,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            raw=response,
        )
