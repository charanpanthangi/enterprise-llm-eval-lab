def tool_misuse_rate(misuses: int, total_tool_steps: int) -> float:
    return 0.0 if total_tool_steps == 0 else misuses / total_tool_steps
