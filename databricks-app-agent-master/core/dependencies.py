from functools import lru_cache
from databricks.sdk import WorkspaceClient
from core.config import get_settings


@lru_cache(maxsize=1)
def get_workspace_client() -> WorkspaceClient:
    """
    WorkspaceClient auto-detects credentials from environment variables
    injected by Databricks Apps (DATABRICKS_HOST, DATABRICKS_CLIENT_ID,
    DATABRICKS_CLIENT_SECRET). Falls back to ~/.databrickscfg for local dev.
    """
    settings = get_settings()
    if settings.databricks_client_id and settings.databricks_client_secret:
        return WorkspaceClient(
            host=settings.databricks_host,
            client_id=settings.databricks_client_id,
            client_secret=settings.databricks_client_secret,
        )
    if settings.databricks_token:
        return WorkspaceClient(
            host=settings.databricks_host,
            token=settings.databricks_token,
        )
    # Falls back to ~/.databrickscfg or env-based auto-detection
    return WorkspaceClient()
