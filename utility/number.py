def get_float(query: str):
    try:
        return float(query)
    except ValueError:
        return None


def get_int(query: str):
    try:
        return int(query)
    except ValueError:
        return None
