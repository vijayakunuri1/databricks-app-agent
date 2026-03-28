from fastapi import APIRouter, Depends
from databricks.sdk import WorkspaceClient
from core.dependencies import get_workspace_client

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live", summary="Liveness check")
def liveness():
    return {"status": "alive"}


@router.get("/ready", summary="Readiness — verifies Databricks connectivity")
def readiness(client: WorkspaceClient = Depends(get_workspace_client)):
    try:
        client.current_user.me()
        return {"status": "ready", "databricks": "connected"}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}
