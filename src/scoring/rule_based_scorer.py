from src.metrics.schema_validation import has_required_fields, is_valid_json


def score_rule_based(output: str, expected_format: str, requires_json: bool, notes: str = "") -> dict:
    score = 1.0
    checks = {}

    checks["length_ok"] = len(output.split()) >= 20
    if not checks["length_ok"]:
        score -= 0.2

    checks["format_hint_present"] = expected_format.split("+")[0].lower() in output.lower() if "markdown" not in expected_format.lower() else True
    if not checks["format_hint_present"]:
        score -= 0.1

    if requires_json:
        checks["json_valid"] = is_valid_json(output)
        if not checks["json_valid"]:
            score -= 0.5
        checks["required_fields"] = has_required_fields(output, ["next_action_plan"]) if "next_action_plan" in notes else True
    else:
        checks["json_valid"] = None
        checks["required_fields"] = None

    forbidden = ["as an ai language model"]
    checks["forbidden_phrases"] = not any(p in output.lower() for p in forbidden)
    if not checks["forbidden_phrases"]:
        score -= 0.2

    return {"rule_score": max(0.0, round(score, 3)), "checks": checks}
