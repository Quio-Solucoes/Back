import unicodedata


def normalizar(txt: str) -> str:
    value = str(txt or "").lower().strip()
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    if value.endswith("s"):
        value = value[:-1]
    return value

