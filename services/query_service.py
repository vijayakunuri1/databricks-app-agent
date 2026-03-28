from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
from core.config import get_settings


class QueryService:
    def __init__(self, client: WorkspaceClient):
        self._client = client
        self._warehouse_id = get_settings().databricks_warehouse_id

    def execute(self, statement: str, catalog: str | None = None) -> dict:
        kwargs: dict = {
            "warehouse_id": self._warehouse_id,
            "statement": statement,
            "wait_timeout": "30s",
        }
        if catalog:
            kwargs["catalog"] = catalog

        response = self._client.statement_execution.execute_statement(**kwargs)

        if response.status.state != StatementState.SUCCEEDED:
            raise RuntimeError(f"Query failed: {response.status.error.message}")

        columns = [c.name for c in response.manifest.schema.columns]
        rows = [
            dict(zip(columns, row))
            for row in (response.result.data_array or [])
        ]
        return {"columns": columns, "rows": rows, "row_count": len(rows)}
