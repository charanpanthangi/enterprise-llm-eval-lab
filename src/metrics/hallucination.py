def hallucination_risk_score(text: str) -> float:
    risky_markers = ["definitely true", "official results of 2028", "confirmed by unknown report"]
    hits = sum(1 for marker in risky_markers if marker.lower() in text.lower())
    return min(1.0, hits / max(1, len(risky_markers)))
