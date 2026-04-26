import json

from src.model_clients.base import BaseModelClient


JUDGE_DIMENSIONS = [
    "accuracy",
    "relevance",
    "completeness",
    "reasoning_quality",
    "instruction_following",
    "clarity",
    "hallucination_risk",
    "enterprise_readiness",
    "client_safe_tone",
    "format_compliance",
]


def judge_output(judge_client: BaseModelClient, prompt: str, output: str) -> dict:
    judge_prompt = (
        "Score the output from 1-5 for each dimension and return strict JSON with keys: "
        f"{JUDGE_DIMENSIONS} and overall_comment.\nPrompt:\n{prompt}\nOutput:\n{output}"
    )
    try:
        response = judge_client.generate(judge_prompt)
        parsed = json.loads(response.content)
        return parsed
    except Exception:  # noqa: BLE001
        return {key: 3 for key in JUDGE_DIMENSIONS} | {"overall_comment": "Fallback score due to judge parse failure."}
