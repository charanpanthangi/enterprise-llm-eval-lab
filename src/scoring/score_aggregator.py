def weighted_score(metrics: dict, weights: dict) -> float:
    score = 0.0
    for k, w in weights.items():
        score += metrics.get(k, 0.0) * w
    return round(score, 4)
