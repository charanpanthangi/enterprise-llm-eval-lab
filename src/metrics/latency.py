def latency_score(seconds: float) -> float:
    if seconds <= 2:
        return 1.0
    if seconds <= 5:
        return 0.8
    if seconds <= 10:
        return 0.6
    return 0.3
