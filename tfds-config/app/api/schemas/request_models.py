from marshmallow import Schema, fields, validate


class ConfigItemSchema(Schema):
    """Schema for a configuration item."""

    name = fields.Str(required=True, description="Configuration name")
    value = fields.Raw(
        required=True, description="Configuration value (can be any type)"
    )
    description = fields.Str(description="Description of this configuration")

    class Meta:
        description = "A single configuration item"
        example = {
            "name": "max_batch_size",
            "value": 64,
            "description": "Maximum batch size for processing",
        }


class ConfigFileSchema(Schema):
    """Schema for a complete configuration file."""

    name = fields.Str(required=True, description="Configuration file name")
    items = fields.List(fields.Nested(ConfigItemSchema), required=True)

    class Meta:
        description = "A configuration file with multiple items"
        example = {
            "name": "training_config",
            "items": [
                {
                    "name": "max_batch_size",
                    "value": 64,
                    "description": "Maximum batch size for processing",
                },
                {
                    "name": "learning_rate",
                    "value": 0.001,
                    "description": "Learning rate for optimizer",
                },
            ],
        }
