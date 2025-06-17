from app.api.schemas.request_models import ConfigFileSchema
from marshmallow import Schema, fields

# Reuse the request schemas for responses where appropriate
ConfigFileResponseSchema = ConfigFileSchema


class ConfigListResponseSchema(Schema):  # type: ignore[misc]
    """Schema for listing available configuration files."""

    configs = fields.List(fields.Str(), metadata={"description": "List of available configuration files"})


class ErrorResponseSchema(Schema):  # type: ignore[misc]
    """Schema for error responses."""

    message = fields.Str(required=True)
    status_code = fields.Int(required=True)

    class Meta:
        description = "Error response"
        example = {"message": "Configuration file not found", "status_code": 404}
