import json


def is_valid_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except Exception:  # noqa: BLE001
        return False


def has_required_fields(text: str, required_fields: list[str]) -> bool:
    try:
        data = json.loads(text)
    except Exception:  # noqa: BLE001
        return False
    return all(field in data for field in required_fields)
