from fastapi import APIRouter
from api.v1 import catalogs, schemas, tables, health, query, chat

api_router = APIRouter()

api_router.include_router(health.router, prefix="/v1")
api_router.include_router(catalogs.router, prefix="/v1")
api_router.include_router(schemas.router, prefix="/v1")
api_router.include_router(tables.router, prefix="/v1")
api_router.include_router(query.router, prefix="/v1")
api_router.include_router(chat.router, prefix="/v1")
