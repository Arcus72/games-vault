import requests
from bcrypt import gensalt, hashpw
from sqlalchemy import func, Integer, nulls_last
from sqlalchemy.orm import Session
from config.settings import Settings, get_settings
from database.models import SteamGames, Genres, Platforms, Languages, Tags, UserGameLibrary
from schemas.schemas import GameFilter, UserLibraryFilters

def gen_password_hash(password: str) -> str:
    salt = gensalt()
    hashed_password = hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def get_filtered_steam_games(db: Session, filters: GameFilter):
    query = db.query(SteamGames)

    if filters.name is not None:
        query = query.filter(func.lower(SteamGames.name).contains(func.lower(filters.name)))
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
    if filters.sorting is not None:
        if filters.sorting.sort_by is not None and filters.sorting.sort_by in SteamGames.__table__.columns.keys():
            sort_column = getattr(SteamGames, filters.sorting.sort_by)
            if filters.sorting.ascending == 1:
                query = query.order_by(nulls_last(sort_column.asc()))
            else:
                query = query.order_by(nulls_last(sort_column.desc()))
    return query.distinct()

def get_searched_games(db: Session, search_query: str):
    query = db.query(SteamGames).filter(func.lower(SteamGames.name).contains(func.lower(search_query)))
    return query

def filter_user_library(user_id: int, db: Session, filters: UserLibraryFilters):
    query = get_filtered_steam_games(db, filters)
    query = query.add_entity(UserGameLibrary)
    query = query.join(UserGameLibrary, UserGameLibrary.appid == SteamGames.appid).filter(UserGameLibrary.user_id == user_id)

    if filters.status is not None:
        query = query.filter(UserGameLibrary.status == filters.status)

    return query.distinct()

def GamesPagination(query, page: int, page_size: int):
    total_games = query.count()
    total_pages = (total_games + page_size - 1) // page_size
    games = query.offset((page - 1) * page_size).limit(page_size).all()
    return games, total_pages

def GET_STEAM64(steam_profile_url: str, settings: Settings = get_settings()):
    if 'https://steamcommunity.com/id/' in steam_profile_url:
        custom_id = steam_profile_url.split('https://steamcommunity.com/id/')[1].replace('/', '')
        STEAMID64 = requests.get('https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={}&vanityurl={}'.format(settings.STEAM_API_KEY, custom_id)).json()
        STEAMID64 = STEAMID64['response']['steamid']
    elif 'https://steamcommunity.com/profiles/' in steam_profile_url:
        STEAMID64 = steam_profile_url.split('https://steamcommunity.com/profiles/')[1].replace('/', '')
    return STEAMID64

def get_steam_library_games_list(steam_id64: str, settings: Settings = get_settings()):
    url = (
        "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&include_appinfo=false&include_played_free_games=1&format=json"
    ).format(settings.STEAM_API_KEY, steam_id64)

    games_id = []
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        games = data['response']['games']

    if not games:
        raise ValueError("Nie znaleziono gier w bibliotece Steam dla podanego uzytkownika.")
    
    for game in games:
        if game['playtime_forever'] > 0:
            games_id.append(game['appid'])
            
    return games_id

    

