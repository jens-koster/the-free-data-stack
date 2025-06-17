from typing import Any

from marshmallow import Schema, ValidationError, fields


def tfds_config_validator(value: Any) -> Any:
    """Custom validator to ensure tfds_config has unique values and only the allowed strings."""
    allowed_set = {"noserve", "noenv"}
    value_set = set(value)

    if len(value) != len(value_set):
        raise ValidationError("Duplicate values are not allowed.")
    diff = value_set.difference(allowed_set)
    if diff:
        raise ValidationError(f"Found {diff}, allowed values are {allowed_set}.")
    return value


class ConfigFileSchema(Schema):  # type: ignore[misc]
    """Schema for a configuration file with metadata."""

    doc = fields.Str(
        required=False,
        metadata={
            "description": "Config documenttion, this is where you document the config values",
        },
    )

    tfds_config = fields.List(
        fields.Str(
            metadata={
                "description": "Allowed values: 'noserve', 'noenv'",
            }
        ),
        validate=tfds_config_validator,
        required=False,
        # this is how we get yaml fields with a dash in them
    )

    # The main configuration dictionary
    config = fields.Dict(
        keys=fields.Str(metadata={"description": "Configuration key"}),
        values=fields.Raw(metadata={"description": "Configuration value (can be any type)"}),
        required=True,
        metadata={"description": "A dictionary of configuration items"},
    )
