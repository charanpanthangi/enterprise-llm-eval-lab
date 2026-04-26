from src.runners.eval_runner import _client_from_config


def run_multiturn(eval_config: dict, models_config: dict) -> list[dict]:
    turns = eval_config["special_tests"].get("multiturn_turns", 10)
    scenario = "You are helping design a sales dashboard. Keep state and apply updated constraints each turn."
    constraints = [
        "Start with SMB segment only.",
        "Now include enterprise too.",
        "Remove any PII fields.",
        "Add weekly granularity.",
        "Budget for implementation is 50k.",
        "Now change budget to 25k.",
        "Need rollout by Q3.",
        "Include risk register.",
        "Use JSON output format.",
        "Summarize final plan in 5 bullets as well.",
    ]
    rows = []
    for model_key in ["model_a", "model_b"]:
        client = _client_from_config(models_config[model_key])
        messages = [{"role": "system", "content": scenario}]
        for i in range(turns):
            user_msg = constraints[i % len(constraints)]
            messages.append({"role": "user", "content": f"Turn {i+1}: {user_msg}"})
            resp = client.generate("", messages=messages)
            messages.append({"role": "assistant", "content": resp.content})
            rows.append({"model_key": model_key, "turn": i + 1, "constraint": user_msg, "response": resp.content})
    return rows
