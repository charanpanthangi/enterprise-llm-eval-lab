def retry_rate(total_retries: int, total_calls: int) -> float:
    return 0.0 if total_calls == 0 else total_retries / total_calls


def error_rate(total_errors: int, total_calls: int) -> float:
    return 0.0 if total_calls == 0 else total_errors / total_calls
