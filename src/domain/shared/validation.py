"""Shared domain validation helpers."""


def require_non_blank_text(*, owner: str, field_name: str, value: str) -> str:
    """Return a normalized non-blank text value or raise a domain validation error."""
    normalized_value = value.strip()
    if normalized_value == "":
        raise ValueError(f"{owner} {field_name} must not be blank")
    return normalized_value


def require_optional_non_blank_text(*, owner: str, field_name: str, value: str | None) -> str | None:
    """Validate optional text values and normalize them when present."""
    return None if value is None else require_non_blank_text(owner=owner, field_name=field_name, value=value)
