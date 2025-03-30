from marshmallow import Schema, fields


class MetaSchema(Schema):
    """Schema for the metadata dictionary."""

    name = fields.Str(
        required=False,
        description="The name of the configuration, overwritten on each call",
        example="training_config",
    )

    notes = fields.Str(
        required=False,
        description="config server generated info, overwritten on each call",
        example="Freshly created from defaults",
    )
    file_name = fields.Str(
        required=False,
        description="The name of the configuration file, overwritten on each call",
        example="training.yaml",
    )


class ConfigFileSchema(Schema):
    """Schema for a configuration file with metadata."""
    doc = fields.Str(
        required=False,
        description="Config documenttion, this is where you document the config values",
        example="url: the url of the s3-ninja server",
    )

    # The main configuration dictionary
    config = fields.Dict(
        keys=fields.Str(description="Configuration key"),
        values=fields.Raw(description="Configuration value (can be any type)"),
        required=True,
        description="A dictionary of configuration items",
        example={
            "max_batch_size": 64,
            "learning_rate": 0.001,
            "num_epochs": 10,
        },
    )
    # Metadata dictionary with strict validation
    meta = fields.Nested(
        MetaSchema,
        required=False,
        description="Metadata about the configuration file",
    )

    class Meta:
        description = "A configuration file with metadata and config"