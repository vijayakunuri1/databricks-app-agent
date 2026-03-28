from fastapi import APIRouter, Depends, HTTPException
from databricks.sdk import WorkspaceClient
from core.dependencies import get_workspace_client
from services.catalog_service import CatalogService

router = APIRouter(prefix="/catalogs", tags=["Catalogs"])


@router.get("/", summary="List all catalogs")
def list_catalogs(client: WorkspaceClient = Depends(get_workspace_client)):
    svc = CatalogService(client)
    return [{"name": c.name, "comment": c.comment} for c in svc.list_catalogs()]


@router.get("/{catalog_name}", summary="Get a catalog")
def get_catalog(catalog_name: str, client: WorkspaceClient = Depends(get_workspace_client)):
    svc = CatalogService(client)
    try:
        c = svc.get_catalog(catalog_name)
        return {"name": c.name, "comment": c.comment, "owner": c.owner}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
