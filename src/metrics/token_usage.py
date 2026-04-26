def token_efficiency(input_tokens: int, output_tokens: int) -> float:
    total = input_tokens + output_tokens
    if total <= 0:
        return 0.0
    return output_tokens / total
