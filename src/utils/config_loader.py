from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv


def load_yaml(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_env() -> None:
    load_dotenv()
