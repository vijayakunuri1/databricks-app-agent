from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from databricks.sdk import WorkspaceClient
from core.dependencies import get_workspace_client
from services.query_service import QueryService

router = APIRouter(prefix="/query", tags=["Query"])


class QueryRequest(BaseModel):
    statement: str
    catalog: str | None = None


@router.post("/", summary="Execute a SQL statement against the catalog")
def execute_query(
    request: QueryRequest,
    client: WorkspaceClient = Depends(get_workspace_client),
):
    svc = QueryService(client)
    try:
        return svc.execute(request.statement, request.catalog)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
