import json

from src.model_clients.base import BaseModelClient


def judge_pairwise(judge_client: BaseModelClient, prompt: str, output_a: str, output_b: str) -> dict:
    blind_prompt = (
        "Compare Output A vs Output B without inferring model identity. "
        "Return strict JSON with keys: winner(A/B/Tie), more_accurate, clearer, safer_to_ship, reason, confidence, category_notes.\n"
        f"Prompt:\n{prompt}\n\nOutput A:\n{output_a}\n\nOutput B:\n{output_b}"
    )
    try:
        response = judge_client.generate(blind_prompt)
        return json.loads(response.content)
    except Exception:  # noqa: BLE001
        return {
            "winner": "Tie",
            "more_accurate": "Tie",
            "clearer": "Tie",
            "safer_to_ship": "Tie",
            "reason": "Fallback due to parse failure.",
            "confidence": "low",
            "category_notes": "n/a",
        }
