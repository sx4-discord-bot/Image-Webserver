def get_float(query: str):
    if not query:
        return None

    try:
        return float(query)
    except ValueError:
        return None


def get_int(query: str):
    if not query:
        return None

    try:
        return int(query)
    except ValueError:
        return None
