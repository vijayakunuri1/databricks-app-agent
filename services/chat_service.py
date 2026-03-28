import json
import re
import time
import logging
import httpx
from openai import OpenAI
from databricks.sdk import WorkspaceClient

from services.catalog_service import CatalogService
from services.query_service import QueryService

logger = logging.getLogger(__name__)

MODEL_NAME = "databricks-meta-llama-3-3-70b-instruct"

SYSTEM_PROMPT = """You are a helpful data assistant with access to a Databricks Unity Catalog.
You can answer questions about catalogs, schemas, tables, and SQL query results.
When the user provides query results, summarize and explain them clearly.
Format tables and lists using markdown."""

SQL_PATTERN = re.compile(
    r"(select|insert|update|delete|create|drop|show|describe|explain|with)\s",
    re.IGNORECASE,
)

_token_cache: dict = {}


class ChatService:
    def __init__(self, client: WorkspaceClient):
        self._client = client
        self._host = client.config.host.rstrip("/")
        self._config = client.config
        self._catalog_svc = CatalogService(client)
        self._query_svc = QueryService(client)

    def _get_token(self) -> str:
        global _token_cache
        if self._config.token:
            return self._config.token
        now = time.time()
        if _token_cache.get("expires_at", 0) > now + 60:
            return _token_cache["access_token"]
        resp = httpx.post(
            f"{self._host}/oidc/v1/token",
            data={"grant_type": "client_credentials", "scope": "all-apis"},
            auth=(self._config.client_id, self._config.client_secret),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        _token_cache = {
            "access_token": data["access_token"],
            "expires_at": now + data.get("expires_in", 3600),
        }
        return data["access_token"]

    def _get_llm(self) -> OpenAI:
        return OpenAI(
            api_key=self._get_token(),
            base_url=f"{self._host}/serving-endpoints",
        )

    def chat(self, messages: list[dict]) -> str:
        last_message = messages[-1]["content"].strip()

        sql = self._extract_sql(last_message)
        if sql:
            return self._handle_sql(sql)

        lower = last_message.lower()
        if "list catalog" in lower or "show catalog" in lower:
            return self._handle_list_catalogs()
        if "list schema" in lower or "show schema" in lower:
            catalog = self._extract_catalog_name(last_message)
            if catalog:
                return self._handle_list_schemas(catalog)
        if "list table" in lower or "show table" in lower:
            return self._handle_list_tables(last_message, messages)

        return self._llm_respond(messages)

    def _extract_sql(self, text: str) -> str | None:
        cleaned = re.sub(r"^(run|execute|query)\s*:\s*", "", text, flags=re.IGNORECASE).strip()
        if SQL_PATTERN.match(cleaned):
            return cleaned
        return None

    def _extract_catalog_name(self, text: str) -> str | None:
        match = re.search(
            r"\b([a-zA-Z0-9_]+)\s+catalog\b|\bcatalog\s+([a-zA-Z0-9_]+)\b", text, re.IGNORECASE
        )
        if match:
            return match.group(1) or match.group(2)
        return None

    def _handle_sql(self, sql: str) -> str:
        try:
            result = self._query_svc.execute(sql)
            if result["row_count"] == 0:
                return "The query ran successfully but returned no rows."
            columns = result["columns"]
            rows = result["rows"]
            header = "| " + " | ".join(columns) + " |"
            separator = "| " + " | ".join(["---"] * len(columns)) + " |"
            body = "\n".join(
                "| " + " | ".join(str(row.get(c, "")) for c in columns) + " |"
                for row in rows[:100]
            )
            return f"**Query returned {result['row_count']} row(s):**\n\n{header}\n{separator}\n{body}"
        except Exception as exc:
            return f"Query failed: {exc}"

    def _handle_list_catalogs(self) -> str:
        try:
            catalogs = self._catalog_svc.list_catalogs()
            names = "\n".join(
                f"- **{c.name}**" + (f" — {c.comment}" if c.comment else "")
                for c in catalogs
            )
            return f"**Available catalogs:**\n\n{names}"
        except Exception as exc:
            return f"Failed to list catalogs: {exc}"

    def _handle_list_schemas(self, catalog: str) -> str:
        try:
            schemas = self._catalog_svc.list_schemas(catalog)
            names = "\n".join(f"- {s.name}" for s in schemas)
            return f"**Schemas in `{catalog}`:**\n\n{names}"
        except Exception as exc:
            return f"Failed to list schemas: {exc}"

    def _handle_list_tables(self, text: str, messages: list[dict]) -> str:
        match = re.search(r"([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)", text)
        if match:
            catalog, schema = match.group(1), match.group(2)
            try:
                tables = self._catalog_svc.list_tables(catalog, schema)
                names = "\n".join(f"- {t.name} ({t.table_type})" for t in tables)
                return f"**Tables in `{catalog}.{schema}`:**\n\n{names}"
            except Exception as exc:
                return f"Failed to list tables: {exc}"
        return self._llm_respond(messages)

    def _llm_respond(self, messages: list[dict]) -> str:
        try:
            llm = self._get_llm()
            api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
            response = llm.chat.completions.create(
                model=MODEL_NAME,
                messages=api_messages,
                temperature=0.1,
                max_tokens=2048,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("LLM call failed: %s", exc)
            return f"I encountered an error: {exc}"
