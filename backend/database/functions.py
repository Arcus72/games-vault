from sqlalchemy import func, Integer
from sqlalchemy.orm import Session
from database.models import SteamGames, Genres, Platforms, Languages, Tags, UserGameLibrary
from schemas.schemas import GameFilter, UserLibraryFilters

def get_filtered_steam_games(db: Session, filters: GameFilter):
    query = db.query(SteamGames)

    if filters.name is not None:
        query = query.filter(SteamGames.name.ilike(f"%{filters.name}%"))
    if filters.release_date_min_year is not None:
        rok = func.split_part(SteamGames.release_date, " ", 3).cast(Integer)
        query = query.filter(rok >= filters.release_date_min_year)
    if filters.release_date_max_year is not None:
        rok = func.split_part(SteamGames.release_date, " ", 3).cast(Integer)
        query = query.filter(rok <= filters.release_date_max_year)
    if filters.price_max is not None:
        query = query.filter(SteamGames.price <= filters.price_max)
    if filters.genres is not None:
        query = query.join(SteamGames.genres).filter(Genres.genre.in_(filters.genres))
    if filters.platforms is not None:
        query = query.join(SteamGames.platforms).filter(Platforms.platform.in_(filters.platforms))
    if filters.languages is not None:
        query = query.join(SteamGames.languages).filter(Languages.language.in_(filters.languages))
    if filters.tags is not None:
        query = query.join(SteamGames.tags).filter(Tags.tag.in_(filters.tags))
    return query.distinct()

def get_searched_games(db: Session, search_query: str):
    query = db.query(SteamGames).filter(SteamGames.name.contains(search_query))
    return query

def filter_user_library(user_id: int, db: Session, filters: UserLibraryFilters):
    query = get_filtered_steam_games(db, filters)
    query = query.add_entity(UserGameLibrary)
    query = query.join(UserGameLibrary, UserGameLibrary.appid == SteamGames.appid).filter(UserGameLibrary.user_id == user_id)

    if filters.library_wishlist is not None:
        query = query.filter(UserGameLibrary.library_wishlist == filters.library_wishlist)
    if filters.hidden is not None:
        query = query.filter(UserGameLibrary.hidden == filters.hidden)

    return query.distinct()
    

