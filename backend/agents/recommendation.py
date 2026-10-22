from typing import Any
import numpy as np

from database.database import get_db
from database.models import SteamGames, Genres, Languages, Tags, Platforms
from schemas.agent_schemas import AgentState
from model_loader import get_embedding_model
from agents.tools import apply_filters


def recommendation_node(state: AgentState) -> AgentState:
    print("recommendation agent")

    active_game = state.get("active_game")
    filters = state.get("filters") or {}

    my_library_ids = [20, 70, 570, 2310, 2320, 3900]  # Przykładowa biblioteka użytkownika

    db = next(get_db())

    try:

        # CONTENT BASED FILTERING

        # Pobranie gier z biblioteki użytkownika
        library_games = (
            db.query(SteamGames.embedding)
            .filter(SteamGames.appid.in_(my_library_ids))
            .filter(SteamGames.embedding.isnot(None))
            .all()
        )

        # Wyciągnięcie embeddingów
        embeddings = [g.embedding for g in library_games if g.embedding is not None]

        # Obliczenie średniego embeddingu (profilu użytkownika)
        if embeddings:
            user_profile = np.mean(np.array(embeddings), axis=0)
        else:
            user_profile = None

        # Normalizacja profilu użytkownika
        norm = np.linalg.norm(user_profile)
        if norm > 0:
            user_profile = user_profile / norm

        # Wykluczenie gier posiadanych przez użytkownika
        query = db.query(SteamGames.appid, SteamGames.name).filter(
            ~SteamGames.appid.in_(my_library_ids)
        )

        # Aplikujemy dodatkowe filtry
        query = apply_filters(query, filters)

        # Pobieramy TOP 5 gier najbardziej podobnych do profilu użytkownika
        matched_games = (
            query.order_by(SteamGames.embedding.cosine_distance(user_profile))
            .limit(5)
            .all()
        )

        # Formatowanie wyników
        results = [game.appid for game in matched_games]
        for matched_game in matched_games:
            print(f"🎯 Znaleziono w bazie: {matched_game.name} (appid: {matched_game.appid})")

        return {"results": results}

        # COLLABORATIVE FILTERING

    except Exception as e:
        print(f"❌ Błąd podczas filtrowania: {e}")
        return {"results": []}
    finally:
        db.close()
