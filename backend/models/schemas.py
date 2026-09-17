from typing import List, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[Message] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str
    tools_used: List[str] = Field(default_factory=list)
    error: Optional[str] = None