from fastapi import APIRouter, Depends, HTTPException, Query
from databricks.sdk import WorkspaceClient
from core.dependencies import get_workspace_client
from services.catalog_service import CatalogService

router = APIRouter(
    prefix="/catalogs/{catalog_name}/schemas/{schema_name}/tables",
    tags=["Tables"],
)


@router.get("/", summary="List tables in a schema")
def list_tables(
    catalog_name: str,
    schema_name: str,
    include_delta_metadata: bool = Query(default=False),
    client: WorkspaceClient = Depends(get_workspace_client),
):
    svc = CatalogService(client)
    try:
        return [
            {
                "name": t.name,
                "full_name": t.full_name,
                "table_type": str(t.table_type),
                "data_source_format": str(t.data_source_format),
            }
            for t in svc.list_tables(catalog_name, schema_name, include_delta_metadata)
        ]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{table_name}", summary="Get table details")
def get_table(
    catalog_name: str,
    schema_name: str,
    table_name: str,
    client: WorkspaceClient = Depends(get_workspace_client),
):
    svc = CatalogService(client)
    try:
        t = svc.get_table(catalog_name, schema_name, table_name)
        return {
            "name": t.name,
            "full_name": t.full_name,
            "table_type": str(t.table_type),
            "columns": [
                {"name": c.name, "type": str(c.type_name), "nullable": c.nullable}
                for c in (t.columns or [])
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
