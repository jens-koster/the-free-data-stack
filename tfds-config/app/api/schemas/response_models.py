from app.api.schemas.request_models import ConfigFileSchema
from marshmallow import Schema, fields

# Reuse the request schemas for responses where appropriate
ConfigFileResponseSchema = ConfigFileSchema


class ConfigListResponseSchema(Schema):
    """Schema for listing available configuration files."""

    configs = fields.List(
        fields.Str(), description="List of available configuration files"
    )

    class Meta:
        description = "List of available configuration files"
        example = {"configs": ["training_config.yaml", "preprocessing_config.yaml"]}


class ErrorResponseSchema(Schema):
    """Schema for error responses."""

    message = fields.Str(required=True, description="Error message")
    status_code = fields.Int(required=True, description="HTTP status code")

    class Meta:
        description = "Error response"
        example = {"message": "Configuration file not found", "status_code": 404}
