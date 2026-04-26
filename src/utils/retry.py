import time
from typing import Callable, TypeVar

T = TypeVar("T")


def with_retry(fn: Callable[[], T], retries: int = 2, backoff_seconds: float = 1.5) -> tuple[T, int]:
    last_err = None
    attempts = 0
    for attempt in range(retries + 1):
        attempts = attempt
        try:
            return fn(), attempts
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            if attempt < retries:
                time.sleep(backoff_seconds * (attempt + 1))
    raise RuntimeError(f"Function failed after retries: {last_err}")
