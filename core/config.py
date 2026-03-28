from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Automatically injected by Databricks Apps runtime
    databricks_host: str = Field(default="")
    databricks_client_id: str = Field(default="")
    databricks_client_secret: str = Field(default="")
    databricks_token: str = Field(default="")
    databricks_app_port: int = Field(default=8000)
    databricks_app_name: str = Field(default="local")
    databricks_workspace_id: str = Field(default="")

    # Bound via app.yaml valueFrom -> resource key
    databricks_warehouse_id: str = Field(default="")
    uc_catalog_name: str = Field(default="main")

    # Application config
    environment: str = Field(default="development")
    log_level: str = Field(default="info")
    app_version: str = Field(default="1.0.0")
    api_secret_key: str = Field(default="")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
