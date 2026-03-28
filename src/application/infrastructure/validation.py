"""Shared infrastructure validation helpers."""


def require_non_blank(*, owner: str, field_name: str, value: str) -> str:
    """Return a normalized non-blank string or raise a descriptive error."""
    normalized_value = value.strip()
    if normalized_value == "":
        raise ValueError(f"{owner} {field_name} must not be blank")
    return normalized_value
