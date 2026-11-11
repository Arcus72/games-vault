from typing import Any
from datetime import date
from rapidfuzz import process, fuzz

from database.models import SteamGames, Genres, Languages, Tags, Platforms, UserGameLibrary
from database.database import get_db
from schemas.schemas import GameFilter


def apply_filters(query, filters: dict):
    """Aplikuje filtry użytkownika do zapytania SQLAlchemy."""
    if not filters:
        return query

    # Jeśli podano obiekt Pydantic, przekształć go na słownik
    if isinstance(filters, GameFilter):
        filters_dict = filters.model_dump(exclude_none=True)
    elif isinstance(filters, dict):
        filters_dict = {k: v for k, v in filters.items() if v is not None}
    else:
        return query

    for filter_name, value in filters_dict.items():
        if value is None or value == "" or value == []:
            continue

        # Filtry ceny
        if filter_name == "price_max":
            query = query.filter(SteamGames.price <= value)

        # Filtry premier
        elif filter_name == "IsReleased":
            if value is True:
                query = query.filter(
                    SteamGames.release_date.isnot(None), SteamGames.release_date != ""
                )
            elif value is False:
                query = query.filter(
                    (SteamGames.release_date.is_(None))
                    | (SteamGames.release_date == "")
                )

        # Filtry dat
        elif filter_name == "release_date_min_year":
            query = query.filter(SteamGames.release_date >= date(int(value), 1, 1))
        elif filter_name == "release_date_max_year":
            query = query.filter(SteamGames.release_date <= date(int(value), 12, 31))

        # Filtry gatunków
        elif filter_name == "genres":
            for genre_name in value:
                query = query.filter(SteamGames.genres.any(Genres.genre.ilike(f"%{genre_name}%")))

        # Filtry języków
        elif filter_name == "languages":
            for lang_name in value:
                query = query.filter(SteamGames.languages.any(Languages.language.ilike(f"%{lang_name}%")))

        # Filtry tagów
        elif filter_name == "tags":
            for tag_name in value:
                query = query.filter(SteamGames.tags.any(Tags.tag.ilike(f"%{tag_name}%")))

        # Filtry platform
        elif filter_name == "platforms":
            for platform_name in value:
                query = query.filter(SteamGames.platforms.any(Platforms.platform.ilike(f"%{platform_name}%")))

    return query


FUZZY_SCORE_THRESHOLD = 70.0

def search_game_id(game_name: str) -> dict[str, Any]:
    """Wyszukuje ID (appid) oraz dokładną nazwę gry w bazie danych."""
    clean_name = (game_name or "").strip()
    if not clean_name:
        return {"status": "error", "message": "Pusta nazwa gry", "appid": None}

    db = next(get_db())
    try:
        # Dopasowanie rozmyte (RapidFuzz)
        games_dict = dict(
            db.query(SteamGames.name, SteamGames.appid)
            .filter(SteamGames.name.isnot(None))
            .all()
        )

        if not games_dict:
            return {
                "status": "not_found",
                "message": "Baza gier jest pusta",
                "appid": None,
            }

        fuzzy_match = process.extractOne(
            clean_name, choices=games_dict.keys(), scorer=fuzz.WRatio
        )

        if fuzzy_match and fuzzy_match[1] >= FUZZY_SCORE_THRESHOLD:
            best_title, score = fuzzy_match[0], fuzzy_match[1]
            ref_id = games_dict[best_title]
            print(
                f"🎯 RapidFuzz Match: '{clean_name}' -> '{best_title}' (appid: {ref_id}, match: {score:.1f}%)"
            )
            return {
                "status": "success",
                "appid": ref_id,
                "matched_name": best_title,
                "searched_query": clean_name,
            }

        print(f"⚠️ Brak lub słabe dopasowanie dla '{clean_name}'")
        return {
            "status": "not_found",
            "message": f"Nie znaleziono gry: {clean_name}",
            "appid": None,
            "searched_query": clean_name,
        }

    except Exception as e:
        print(f"❌ Błąd w search_game_id: {e}")
        return {"status": "error", "message": str(e), "appid": None}
    finally:
        db.close()


def get_user_library(user_id: int):
    if user_id is None:
        return []

    db = next(get_db())

    library_games = (
        db.query(UserGameLibrary.appid)
        .filter(UserGameLibrary.user_id == user_id)
        .all()
    )

    return [appid for (appid,) in library_games]


def merge_filters(
    message_filters: GameFilter | dict | None,
    config_filters: GameFilter | dict | None,
) -> GameFilter:
    # Standaryzacja do instancji GameFilter
    msg_filters = (
        message_filters
        if isinstance(message_filters, GameFilter)
        else GameFilter(**(message_filters or {}))
    )
    cfg_filters = (
        config_filters
        if isinstance(config_filters, GameFilter)
        else GameFilter(**(config_filters or {}))
    )

    # Pobranie filtrów z wiadomości i nadpisanie ich filtrami z config
    merged_filters = cfg_filters.model_dump(exclude_none=True) | msg_filters.model_dump(exclude_none=True)

    return GameFilter(**merged_filters)
