from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    email: str
    phone: str
    password: str

class UserLogin(BaseModel): 
    username_or_email: str
    password: str

class GameFilter(BaseModel):
    name: str | None = None
    genres: list[str] | None = None
    languages: list[str] | None = None
    tags: list[str] | None = None
    platforms: list[str] | None = None
    price_max: int | None = None
    IsReleased: bool | None = None
    release_date_min_year: int | None = None
    release_date_max_year: int | None = None

class UserLibraryFilters(GameFilter):
    library_wishlist: int | None = None    #    None -> Wszystkie Gry, 0 -> Biblioteka, 1 -> Wishlista
    hidden: int | None = None              #    None -> Wszystkie, 0 -> tylko nie ukryte, 1 -> tylko ukryte

class GameSearchRespone(BaseModel):
    appid: int
    name: str
    capsule_image: str

class GameRespone(BaseModel):
    appid: int
    name: str
    price: float
    release_date: str | None
    header_image: str
    library_wishlist: int | None #1 -> biblioteka , 2 -> lista_życzeń
    isHidden: int | None

    model_config = ConfigDict(from_attributes=True)

class GamesFilterRespone(BaseModel):
    games: list[GameRespone]
    page: int
    pages: int 


