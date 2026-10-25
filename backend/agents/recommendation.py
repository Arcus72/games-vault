import numpy as np
from langchain_core.runnables import RunnableConfig

from database.database import get_db
from database.models import SteamGames
from schemas.agent_schemas import AgentState
from agents.tools import apply_filters, search_game_id, get_user_library


REFERENCES_SCORE = 0.7
LIBRARY_SCORE = 0.3


def recommendation_node(state: AgentState, config: RunnableConfig) -> AgentState:
    print("recommendation agent")

    filters = state.get("filters") or {}

    # Pobranie biblioteki użytkownika
    user_id = config.get("configurable", {}).get("user_id")
    library_ids = get_user_library(user_id) 

    # Wyszukiwanie gier referencyjnych
    references = state.get("references") or []

    references_ids = []
    for reference in references:
        if not isinstance(reference, str) or not reference.strip():
            continue

        game = search_game_id(reference)
        if game.get("status") == "success" and game.get("appid") is not None:
            references_ids.append(game["appid"])

    db = next(get_db())

    try:

        # Pobranie embeddingów gier referencyjnych
        ref_embeddings = []
        if references_ids:
            games = (
                db.query(SteamGames.embedding)
                .filter(SteamGames.appid.in_(references_ids))
                .filter(SteamGames.embedding.isnot(None))
                .all()
            )
            ref_embeddings = [g.embedding for g in games if g.embedding is not None]

        # Pobranie gier z biblioteki użytkownika
        lib_embeddings = []
        if library_ids:
            games = (
                db.query(SteamGames.embedding)
                .filter(SteamGames.appid.in_(library_ids))
                .filter(SteamGames.embedding.isnot(None))
                .all()
            )
            lib_embeddings = [g.embedding for g in games if g.embedding is not None]

        # Obliczenie profilu użytkownika (kombinacja liniowa 0.7 ref + 0.3 lib)
        ref_profile = np.mean(ref_embeddings, axis=0) if ref_embeddings else None
        lib_profile = np.mean(lib_embeddings, axis=0) if lib_embeddings else None

        if ref_profile is not None and lib_profile is not None:
            user_profile = 0.7 * ref_profile + 0.3 * lib_profile   # Gdy są obecne OBA źródła: wagi 0.7 i 0.3
        elif ref_profile is not None:
            user_profile = ref_profile  # Tylko gry referencyjne
        elif lib_profile is not None:
            user_profile = lib_profile  # Tylko biblioteka
        else:
            return {"results": []}  # Brak jakichkolwiek embeddingów do obliczeń

        # Normalizacja profilu użytkownika
        norm = np.linalg.norm(user_profile)
        if norm > 0:
            user_profile = user_profile / norm

        # Wykluczenie gier posiadanych przez użytkownika lub referencyjnych
        excluded_ids = set((library_ids or []) + (references_ids or []))
        query = db.query(SteamGames.appid, SteamGames.name)

        if excluded_ids:
            query = query.filter(~SteamGames.appid.in_(excluded_ids))

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
