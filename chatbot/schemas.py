from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    message_intent: str | None
    filters: dict[str, Any]

    results: list[dict[str, Any]]


class Filters(BaseModel):
    genres: list[str] | None = None
    platforms: list[str] | None = None
    max_price: str | None = None
    min_price: str | None = None
    min_rating: str | None = None
    release_after: str | None = None
    language: list[str] | None = None


class IntentClassifier(BaseModel):
    message_intent: Literal["recommendation", "semantic_search"] = Field(..., description="Classify whether the user wants recommendation or semantic_search.")
    reference_game: str | None = None
    filters: Filters = Field(default_factory=Filters)