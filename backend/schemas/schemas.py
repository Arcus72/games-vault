from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel): 
    username_or_email: str
    password: str

class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str

class GameFilter(BaseModel):
    page: int = 1
    name: str | None = None
    genres: list[str] | None = None
    languages: list[str] | None = None
    tags: list[str] | None = None
    platforms: list[str] | None = None
    price_max: int | None = None
    IsReleased: bool | None = None
    release_date_min_year: int | None = None
    release_date_max_year: int | None = None
    sort_by: str | None = None  
    ascending: int | None = None

class UserLibraryFilters(GameFilter):
    status: int | None = None              # 0 -> Brak 1 -> Wishlist 2 -> Library 3 -> Library_Hidden

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
    status: int | None   # 0 -> Brak 1 -> Wishlist 2 -> Library 3 -> Library_Hidden

    model_config = ConfigDict(from_attributes=True)

class GamesFilterRespone(BaseModel):
    games: list[GameRespone]
    page: int
    pages: int 

