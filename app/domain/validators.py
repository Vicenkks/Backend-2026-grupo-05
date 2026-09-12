def validate_text(value: str, field_name: str) -> str:
    # Validates that a text is not empty and returns it cleaned.
    if not value or not str(value).strip():
        raise ValueError(f"The {field_name} is required")
    return str(value).strip()