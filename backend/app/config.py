from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = Field(
        default="dev",
        validation_alias=AliasChoices("APP_ENV", "ENVIRONMENT"),
    )
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.8-flash", alias="GEMINI_MODEL")

    supabase_url: str | None = Field(default=None, alias="SUPABASE_URL")
    supabase_service_role_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_KEY"),
    )

    max_message_length: int = Field(
        default=10000,
        validation_alias=AliasChoices("MAX_MESSAGE_LENGTH", "MAX_MESSAGE_CHARS"),
    )
    max_tool_calls: int = Field(default=6, alias="MAX_TOOL_CALLS")
    max_tool_result_bytes: int = Field(default=100000, alias="MAX_TOOL_RESULT_BYTES")
    request_timeout_seconds: int = Field(default=30, alias="REQUEST_TIMEOUT_SECONDS")

    rate_limit_per_minute: int = Field(default=30, alias="RATE_LIMIT_PER_MINUTE")

    proposal_expiry_minutes: int = Field(default=60, alias="PROPOSAL_EXPIRY_MINUTES")

    cors_origins: list[str] = Field(
        default=["*"],
        alias="CORS_ORIGINS",
    )


settings = Settings()
