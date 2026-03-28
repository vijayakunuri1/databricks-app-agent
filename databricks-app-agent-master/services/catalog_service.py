from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import CatalogInfo, SchemaInfo, TableInfo


class CatalogService:
    def __init__(self, client: WorkspaceClient):
        self._client = client

    def list_catalogs(self) -> list[CatalogInfo]:
        return list(self._client.catalogs.list())

    def get_catalog(self, catalog_name: str) -> CatalogInfo:
        return self._client.catalogs.get(catalog_name)

    def list_schemas(self, catalog_name: str) -> list[SchemaInfo]:
        return list(self._client.schemas.list(catalog_name=catalog_name))

    def get_schema(self, catalog_name: str, schema_name: str) -> SchemaInfo:
        return self._client.schemas.get(full_name=f"{catalog_name}.{schema_name}")

    def list_tables(
        self,
        catalog_name: str,
        schema_name: str,
        include_delta_metadata: bool = False,
    ) -> list[TableInfo]:
        return list(
            self._client.tables.list(
                catalog_name=catalog_name,
                schema_name=schema_name,
                include_delta_metadata=include_delta_metadata,
            )
        )

    def get_table(self, catalog_name: str, schema_name: str, table_name: str) -> TableInfo:
        return self._client.tables.get(
            full_name=f"{catalog_name}.{schema_name}.{table_name}"
        )
