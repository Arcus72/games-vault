import numpy as np
from langchain_core.runnables import RunnableConfig
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import SteamGames
from schemas.agent_schemas import AgentState
from agents.tools import apply_filters, search_game_id, search_game_id_by_vector, get_user_library
from model_loader import get_als_recommendations


def resolve_reference_ids(references: list) -> list[int]:
    """Zamienia nazwy gier referencyjnych na listę poprawnych Steam appid."""
    ref_ids = []

    for ref in references or []:
        if isinstance(ref, str) and ref.strip():
            # game = search_game_id(ref)
            game = search_game_id_by_vector(ref)
            if game.get("status") == "success" and game.get("appid") is not None:
                ref_ids.append(int(game["appid"]))
    return list(dict.fromkeys(ref_ids))


def build_user_profile(
    db: Session,
    references_ids: list[int],
    library_ids: list[int],
    ref_weight: float = 0.7,
) -> np.ndarray | None:
    """
    Pobiera embeddingi jednym zapytaniem SQL i buduje znormalizowany wektor profilu użytkownika.
    Zwraca None, jeśli brak jakichkolwiek embeddingów.
    """
    all_ids = set(references_ids) | set(library_ids)
    if not all_ids:
        return None

    rows = (
        db.query(SteamGames.appid, SteamGames.embedding)
        .filter(SteamGames.appid.in_(all_ids), SteamGames.embedding.isnot(None))
        .all()
    )
    emb_map = {r.appid: np.asarray(r.embedding, dtype=np.float32) for r in rows}

    ref_embs = [emb_map[aid] for aid in references_ids if aid in emb_map]
    lib_embs = [emb_map[aid] for aid in library_ids if aid in emb_map]

    ref_profile = np.mean(ref_embs, axis=0) if ref_embs else None
    lib_profile = np.mean(lib_embs, axis=0) if lib_embs else None

    if ref_profile is not None and lib_profile is not None:
        profile = ref_weight * ref_profile + (1.0 - ref_weight) * lib_profile
    elif ref_profile is not None:
        profile = ref_profile
    elif lib_profile is not None:
        profile = lib_profile
    else:
        return None

    norm = np.linalg.norm(profile)
    return (profile / norm) if norm > 0 else None


def get_popular_fallback(db: Session, filters: dict, excluded_ids: set[int], limit: int = 5) -> list[int]:
    """Zwraca najpopularniejsze gry, respektując filtry i wykluczenia."""
    print("ℹBrak biblioteki i referencji — zwracam najpopularniejsze gry.")
    query = db.query(SteamGames.appid, SteamGames.name, SteamGames.popularity)

    if excluded_ids:
        query = query.filter(~SteamGames.appid.in_(excluded_ids))

    query = apply_filters(query, filters)
    games = (
        query.filter(SteamGames.popularity.isnot(None))
        .order_by(SteamGames.popularity.desc())
        .limit(limit)
        .all()
    )

    for g in games:
        print(f"🔥 Popularna gra: {g.name} (appid: {g.appid}, popularity: {g.popularity})")
    return [g.appid for g in games]


def rank_hybrid_candidates(candidate_games: list, user_id: int | None, top_n: int = 5) -> list[int]:
    """Łączy wynik Content-Based (distance) z Collaborative Filtering (ALS) i zwraca TOP N."""
    cf_scores_map = get_als_recommendations(user_id, N=1000) if user_id is not None else {}
    alpha = 0.6 if cf_scores_map else 1.0

    scored = []
    for game in candidate_games:
        content_score = max(0.0, 1.0 - float(game.distance))
        cf_score = cf_scores_map.get(game.appid, 0.0)
        hybrid_score = alpha * content_score + (1.0 - alpha) * cf_score
        scored.append((game.appid, game.name, hybrid_score, content_score, cf_score))

    scored.sort(key=lambda x: x[2], reverse=True)
    top_games = scored[:top_n]

    for appid, name, h_score, c_score, cf_s in top_games:
        print(
            f"🎯 Znaleziono: {name} (appid: {appid}) | "
            f"Hybrid: {h_score:.3f} (Content: {c_score:.3f}, CF: {cf_s:.3f})"
        )
    return [g[0] for g in top_games]


def recommendation_node(state: AgentState, config: RunnableConfig) -> AgentState:
    print("recommendation agent")

    filters = state.get("filters") or {}
    user_id = config.get("configurable", {}).get("user_id")
    library_ids = get_user_library(user_id) or []
    references_ids = resolve_reference_ids(state.get("references") or [])
    excluded_ids = set(library_ids) | set(references_ids)

    db = next(get_db())

    try:
        user_profile = build_user_profile(db, references_ids, library_ids)

        # Gdy brak profilu użytkownika (brak referencji i/lub biblioteki), zwracamy najpopularniejsze gry
        if user_profile is None:
            return {"results": get_popular_fallback(db, filters, excluded_ids, limit=5)}

        # Pobranie kandydatów z Content-Based Filtering
        distance_col = SteamGames.embedding.cosine_distance(user_profile).label("distance")
        query = db.query(SteamGames.appid, SteamGames.name, distance_col)

        if excluded_ids:
            query = query.filter(~SteamGames.appid.in_(excluded_ids))

        query = apply_filters(query, filters)
        candidate_games = query.order_by(distance_col).limit(500).all()

        if not candidate_games:
            return {"results": []}

        return {"results": rank_hybrid_candidates(candidate_games, user_id, top_n=5)}

    except Exception as e:
        print(f"❌ Błąd podczas rekomendacji: {e}")
        return {"results": []}