def boolean(value):
    if not value:
        return False

    if isinstance(value, str):
        return str(value).lower() == "true"

    return False
