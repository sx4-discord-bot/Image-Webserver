from typing import Optional


def get_float(query: str) -> Optional[float]:
    if not query:
        return None

    try:
        return float(query)
    except ValueError:
        return None


def get_int(query: str) -> Optional[int]:
    if not query:
        return None

    try:
        return int(query)
    except ValueError:
        return None
