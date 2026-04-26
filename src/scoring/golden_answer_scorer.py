def _token_set(text: str) -> set[str]:
    return set(t.strip(".,:;!?()[]{}\"'").lower() for t in text.split() if t.strip())


def score_golden(output: str, golden_answer: str) -> dict:
    if not golden_answer:
        return {"exact_match": 0.0, "overlap": 0.0, "golden_score": 0.0}
    exact = 1.0 if output.strip() == golden_answer.strip() else 0.0
    output_tokens = _token_set(output)
    golden_tokens = _token_set(golden_answer)
    overlap = 0.0 if not golden_tokens else len(output_tokens & golden_tokens) / len(golden_tokens)
    score = 0.6 * exact + 0.4 * overlap
    return {"exact_match": exact, "overlap": round(overlap, 3), "golden_score": round(score, 3)}
