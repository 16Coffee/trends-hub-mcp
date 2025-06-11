from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, List
from pydantic import BaseModel, Field


class MCPMessage(BaseModel):
    id: str
    type: Literal["request", "response", "error"]
    action: str
    payload: Any = Field(default_factory=dict)
    ts: datetime


class NewsItem(BaseModel):
    title: str
    link: str
    published: str | None = None
    summary: str | None = None


class HotNewsPayload(BaseModel):
    items: List[NewsItem]
