def estimate_cost(input_tokens: int, output_tokens: int, input_cost: float, output_cost: float) -> float:
    return (input_tokens * input_cost) + (output_tokens * output_cost)
