from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from schemas.schemas import GameFilter


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    message_intent: str | None

    active_game: str | None
    filters: GameFilter | None

    results: list[dict[str, Any]]


class IntentClassifier(BaseModel):
    message_intent: Literal["recommendation", "semantic_search", "game_info"] = Field(
        ...,
        description="Classify whether the user wants recommendation, semantic_search, or game_info.",
    )
    active_game: str | None = None
    filters: GameFilter = Field(default_factory=GameFilter)
