import re


def anonymize_text(text: str) -> str:
    text = re.sub(r"[\w\.-]+@[\w\.-]+", "[EMAIL]", text)
    text = re.sub(r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b", "[SENSITIVE_ID]", text)
    return text
