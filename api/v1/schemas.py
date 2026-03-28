from fastapi import APIRouter, Depends, HTTPException
from databricks.sdk import WorkspaceClient
from core.dependencies import get_workspace_client
from services.catalog_service import CatalogService

router = APIRouter(prefix="/catalogs/{catalog_name}/schemas", tags=["Schemas"])


@router.get("/", summary="List schemas in a catalog")
def list_schemas(
    catalog_name: str,
    client: WorkspaceClient = Depends(get_workspace_client),
):
    svc = CatalogService(client)
    try:
        return [
            {"name": s.name, "catalog": s.catalog_name, "comment": s.comment}
            for s in svc.list_schemas(catalog_name)
        ]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{schema_name}", summary="Get a schema")
def get_schema(
    catalog_name: str,
    schema_name: str,
    client: WorkspaceClient = Depends(get_workspace_client),
):
    svc = CatalogService(client)
    try:
        s = svc.get_schema(catalog_name, schema_name)
        return {"name": s.name, "catalog": s.catalog_name, "full_name": s.full_name}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
