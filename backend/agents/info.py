from typing import Any
from rapidfuzz import process, fuzz
from database.database import get_db
from database.models import SteamGames
from schemas.agent_schemas import AgentState

from agents.tools import search_game_id


def info_node(state: AgentState) -> dict[str, Any]:
    print("info agent")

    references = state.get("references") or []

    if not references:
        print("⚠️ Brak gier w polu 'references'.")
        return {"results": []}

    matched_ids = []

    for reference in references:
        if not isinstance(reference, str) or not reference.strip():
            continue

        game = search_game_id(reference)
        if game.get("status") == "success" and game.get("appid") is not None:
            matched_ids.append(game["appid"])

    return {"results": matched_ids}
