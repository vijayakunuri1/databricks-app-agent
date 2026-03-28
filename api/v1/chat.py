from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from databricks.sdk import WorkspaceClient

from core.dependencies import get_workspace_client
from services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)


class ChatResponse(BaseModel):
    message: str


@router.post("/", response_model=ChatResponse, summary="Chat with the Unity Catalog AI assistant")
def chat(
    request: ChatRequest,
    client: WorkspaceClient = Depends(get_workspace_client),
):
    svc = ChatService(client)
    try:
        messages = [m.model_dump() for m in request.messages]
        reply = svc.chat(messages)
        return ChatResponse(message=reply)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
