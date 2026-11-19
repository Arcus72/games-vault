from schemas.agent_schemas import AgentState
from database.database import get_db
from database.models import SteamGames
from agents.tools import apply_filters


def releases_node(state: AgentState) -> AgentState:
    print("releases agent")

    db = next(get_db())
    filters = state.get("filters") or {}
    num_of_results = state.get("number_of_results")

    try:
        query = db.query(SteamGames.appid, SteamGames.name)
        query = apply_filters(query, filters)
        
        releases = (
            query.filter(SteamGames.is_released == 0)
            .limit(num_of_results)
            .all()
        )

        results = [game.appid for game in releases]
        for release in releases:
            print(
                f"🎯 Znaleziono w bazie: {release.name} (appid: {release.appid})"
            )

        return {"results": results}

    except Exception as e:
        print(f"❌ Błąd w releases_node: {e}")
        return {"results": []}
    finally:
        db.close()
