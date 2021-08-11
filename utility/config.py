import json
from typing import Any

config = json.load(open("config.json"))


def get(key: str) -> Any:
    return config[key]
