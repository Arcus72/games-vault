from schemas.agent_schemas import AgentState

from database.database import get_db
from model_loader import get_embedding_model
from database.models import SteamGames

def semantic_search_node(state: AgentState) -> AgentState:
    print("semantic search agent")

    db = next(get_db())
    embedding_model = get_embedding_model()

    try:
        query_vector = embedding_model.encode(
            state["messages"][-1].content, normalize_embeddings=True
        ).tolist()

        matched_games = (
            db.query(SteamGames.appid, SteamGames.name)
            .order_by(SteamGames.embedding.cosine_distance(query_vector))
            .limit(3)
            .all()
        )

        results = [{"id": game.appid, "name": game.name} for game in matched_games]
        for matched_game in matched_games:
            print(
                f"🎯 Znaleziono w bazie: {matched_game.name} (appid: {matched_game.appid})"
            )

        return {"results": results}

    except Exception as e:
        print(f"❌ Błąd w info_node: {e}")
        return {"results": []}
    finally:
        db.close()
