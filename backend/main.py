import uuid
import hashlib
import base64
from math import ceil
from bcrypt import hashpw, gensalt, checkpw
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from sqlalchemy import null, and_
from sqlalchemy.orm import Session
from database.database import get_db
from auth.user_auth import authenticate_session, create_new_session, authenticate_user, attach_user_to_session
from database.functions import get_filtered_steam_games, get_searched_games, filter_user_library
from database.models import Users, UserSession, SteamGames, SteamLanguages, SteamGenres, SteamTags, SteamPlatforms, UserGameLibrary, Tags, Platforms, Genres, Languages
from fastapi.middleware.cors import CORSMiddleware
from schemas.schemas import GameFilter, GamesFilterRespone, UserCreate, UserLogin, GameSearchRespone, GameRespone, UserLibraryFilters, GamesRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#zostawiam w razie czego ale jest nie potrzebna bo każdy endpoint ma Depends(authenticate_session) ewentualnie można wrzucić przy wejściu na strone
@app.get("/api/set_user_session")
def set_user_session(response: Response, session: UserSession = Depends(authenticate_session), db: Session = Depends(get_db)):
    if not session:
        new_session = create_new_session(response, db, user_id = None)
        return {"message": "New user session created.", "session_id": new_session.session_id}
    return {"message": "User session set successfully."}

@app.get("/api/get_user_session")

def get_user_session(session: UserSession = Depends(authenticate_session)):
    if session:
        return {"session_id": session.session_id, "user_id": session.user_id}
    else:
        raise HTTPException(status_code=401, detail="Sesja użytkownika nie została znaleziona lub wygasła.")

@app.get("/api/get_user_info")
def get_user_info(user_session: UserSession = Depends(authenticate_user)):
    if user_session.user:
        return {"user_id": user_session.user.id
                , "username": user_session.user.username
                , "email": user_session.user.email
                , "phone": user_session.user.phone
                , "session_id": user_session.session_id}
    return {"message": "Użytkownik nie jest zalogowany."}

@app.post("/api/create_user")
async def create_user(request: Request, data: UserCreate, session: UserSession = Depends(authenticate_session), db: Session = Depends(get_db)):
    username = data.username
    email = data.email
    phone = data.phone
    password = data.password

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="Missing required fields.")

    existing_user = db.query(Users).filter((Users.username == username) | (Users.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Użytkownik o podanej nazwie użytkownika lub adresie e-mail już istnieje.")
    
    salt = gensalt()
    hashed_password = hashpw(password.encode('utf-8'), salt)
    hashed_password = hashed_password.decode('utf-8')
    new_user = Users(username=username, email=email, phone=phone, password_hash=hashed_password, active=1)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Użytkownik utworzony pomyślnie. Teraz możesz się zalogować.", "user_id": new_user.id}

@app.put("/api/login")
async def login(request: Request, response: Response, data: UserLogin, db: Session = Depends(get_db), session: UserSession = Depends(authenticate_session)):
    if session and session.user_id is not None:
        return {"message": "Użytkownik jest już zalogowany.", "user_id": session.user_id}
    username_or_email = data.username_or_email
    password = data.password

    if not username_or_email or not password:
        raise HTTPException(status_code=400, detail="Brakujące wymagane pola.")
    user = db.query(Users).filter((Users.username == username_or_email) | (Users.email == username_or_email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Błędny mail lub hasło.")
    elif not user.active:
        raise HTTPException(status_code=403, detail="Konto jest niekatywne.")
    elif not checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Błędny mail lub hasło.")
    
    attach_user_to_session(session.session_id, user.id, db)
    return {"message": "Zalogowano pomyślnie.", "user_id": user.id}

@app.delete("/api/logout")
def logout(response: Response, user_session: UserSession = Depends(authenticate_user), db: Session = Depends(get_db)):
    if user_session.user_id is None:
        raise HTTPException(status_code=401, detail="Użytkownik nie jest zalogowany.")

    db.delete(user_session)
    db.commit()
    response.delete_cookie(key="user_session_id")
    return {"message": "Wylogowano pomyślnie."}

@app.post("/api/get_steam_games", response_model=GamesFilterRespone)
def get_steam_games(body: GamesRequest, session: UserSession = Depends(authenticate_session), db: Session = Depends(get_db)) -> GamesFilterRespone:
    page = body.page
    filters = body.filters or GameFilter()
    page_size = 30
    if not page or page < 1:
        page = 1
    query = get_filtered_steam_games(db, filters).order_by(SteamGames.recommendations.desc())
    if session.user_id is not None:
        query = query.outerjoin(
            UserGameLibrary,
            and_(
                UserGameLibrary.appid == SteamGames.appid,
                UserGameLibrary.user_id == session.user_id
            )
        ).add_entity(UserGameLibrary)
    total_games = query.count()
    total_pages = ceil(total_games / page_size)
    offset = (page - 1) * page_size
    games = query.offset(offset).limit(page_size).all()
    if session.user_id is not None:
            games_result = [
                GameRespone(
                    appid=game.appid,
                    name=game.name,
                    price=game.price,
                    release_date=game.release_date,
                    header_image=game.header_image_url,
                    library_wishlist=lib.library_wishlist if lib else 0,
                    isHidden=lib.hidden if lib else 0,
                )
                for game, lib in games
            ]
    else:
        games_result = [
            GameRespone(
                appid=game.appid,
                name=game.name,
                price=game.price,
                release_date=game.release_date,
                header_image=game.header_image_url,
                library_wishlist=None,
                isHidden=None,
            )
            for game in games
        ]

    return GamesFilterRespone(
        games=games_result,
        page=page,
        pages=total_pages,
    )

@app.post("/api/get_user_library", response_model=GamesFilterRespone)
def get_user_library(page: int = 1, db: Session = Depends(get_db), user_session: UserSession = Depends(authenticate_user), filters: UserLibraryFilters = Depends()):
    if not page or page < 1:
        page = 1

    page_size = 30
    user_id = user_session.user.id
    query_user_library = filter_user_library(user_id, db, filters).order_by(SteamGames.recommendations.desc())
    total_games = query_user_library.count()
    total_pages = ceil(total_games / page_size)
    offset = (page - 1) * page_size
    user_library = query_user_library.offset(offset).limit(page_size).all()
    if not user_library:
        raise HTTPException(status_code=404, detail="Nie znaleziono gier w bibliotece użytkownika.")

    library_result = [
        GameRespone(
            appid=game.appid,
            name=game.name,
            price=game.price,
            release_date=game.release_date,
            header_image=game.header_image_url,
            library_wishlist=lib.library_wishlist,
            isHidden=lib.hidden,
        ) for game, lib in user_library
    ]

    return GamesFilterRespone(
        games=library_result,
        page=page,
        pages=total_pages,
    )

@app.get("/api/games_search_bar")
def games_search_bar(filter: str, session: UserSession = Depends(authenticate_session), db: Session = Depends(get_db)):
    if filter is None or filter.strip() == "":
        raise HTTPException(status_code=400, detail="Searchbar jest pusty. Wprowadź nazwę gry lub jej fragment.")
    page_size = 6
    query = get_searched_games(db, filter)
    games = query.order_by(SteamGames.recommendations.desc()).limit(page_size).all()

    if not games:
        raise HTTPException(status_code=400, detail="Nie znaleziono gier.")
    return [
        GameSearchRespone(
            appid=game.appid,
            name=game.name,
            capsule_image=game.capsule_image_url
        ) for game in games
    ]

@app.get("/api/get_tags")
def get_tags(db: Session = Depends(get_db), session: UserSession = Depends(authenticate_session)):
    tags = db.query(Tags).order_by(Tags.tag.asc()).all()
    return [tag.tag for tag in tags]

@app.get("/api/get_platforms")
def get_platforms(db: Session = Depends(get_db), session: UserSession = Depends(authenticate_session)):
    platforms = db.query(Platforms).order_by(Platforms.platform.asc()).all()
    return [platform.platform for platform in platforms]

@app.get("/api/get_genres")
def get_genres(db: Session = Depends(get_db), session: UserSession = Depends(authenticate_session)):
    genres = db.query(Genres).order_by(Genres.genre.asc()).all()
    return [genre.genre for genre in genres]

@app.get("/api/get_languages")
def get_languages(db: Session = Depends(get_db), session: UserSession = Depends(authenticate_session)):
    languages = db.query(Languages).order_by(Languages.language.asc()).all()
    return [language.language for language in languages]


@app.post("/api/add_game_to_library")
def add_game_to_library(app_id: int, user_session: UserSession = Depends(authenticate_user), db: Session = Depends(get_db)):
    user_id = user_session.user_id
    if app_id and user_id:
        library = db.query(UserGameLibrary).filter(UserGameLibrary.user_id == user_id).filter(UserGameLibrary.appid == app_id).filter(UserGameLibrary.library_wishlist == 1).count()
        wishlist = db.query(UserGameLibrary).filter(UserGameLibrary.user_id == user_id).filter(UserGameLibrary.appid == app_id).filter(UserGameLibrary.library_wishlist == 2).first()
        if library > 0:
            raise HTTPException(status_code=404, detail="Gra już jest w bibliotece")
        elif wishlist:
            wishlist.library_wishlist = 1
            db.commit()
            return {"message": "Zaktualizowano"}
        elif not wishlist and library == 0:
            new_lib_game = UserGameLibrary(user_id=user_id,appid=app_id,library_wishlist=1,hidden=0)
            db.add(new_lib_game)
            db.commit()
            db.refresh(new_lib_game)
            return {"message": "Dodano do biblioteki"}
        raise HTTPException(status_code=404, detail="Błąd przetawrzania")
        

@app.post("/api/add_game_to_wishlist")
def add_game_to_library(app_id: int, user_session: UserSession = Depends(authenticate_user), db: Session = Depends(get_db)):
    user_id = user_session.user_id
    if app_id and user_id:
        wishlist = db.query(UserGameLibrary).filter(UserGameLibrary.user_id == user_id).filter(UserGameLibrary.appid == app_id).filter(UserGameLibrary.library_wishlist == 2).first()
        library = db.query(UserGameLibrary).filter(UserGameLibrary.user_id == user_id).filter(UserGameLibrary.appid == app_id).filter(UserGameLibrary.library_wishlist == 1).count()
        if library > 0:
            raise HTTPException(status_code=404, detail="Nie można dodać do listy życzeń gdy gra jest w bibliotece")
        elif wishlist:
            db.delete(wishlist)
            db.commit()
            raise HTTPException(status_code=404, detail="Usunięto z listy życzeń")
        elif library == 0 and not wishlist:
            new_wish_game = UserGameLibrary(user_id=user_id,appid=app_id,library_wishlist=2,hidden=0)
            db.add(new_wish_game)
            db.commit()
            db.refresh(new_wish_game)
            return {"message": "Dodano do listy życzeń"}
        raise HTTPException(status_code=404, detail="Błąd przetawrzania")

@app.post("/api/hide_game")
def add_game_to_library(app_id: int, user_session: UserSession = Depends(authenticate_user), db: Session = Depends(get_db)):
    user_id = user_session.user_id
    if app_id and user_id:
        lib = db.query(UserGameLibrary).filter(UserGameLibrary.user_id == user_id).filter(UserGameLibrary.appid == app_id).filter(UserGameLibrary.library_wishlist == 1).first()
        if lib:
            lib.hidden = 1 - lib.hidden
            db.commit()
            return {"message": "ukryto grę"}
        elif not lib:
            return {"message": "Nie ma takiej gry w bibliotece"}
        raise HTTPException(status_code=404, detail="Błąd przetawrzania")


@app.post("/api/message")
def get_message(data: dict, session: UserSession = Depends(authenticate_session), db: Session = Depends(get_db)):
    user_message = data.get("question", "")
    print("User message:", user_message)
    return {
        "success": True,
        "response": "This is the list of games that will suit you best:",
        "games": [
            {
            "appid": "g-9842",
            "title": "The Witcher 3: Wild Hunt",
            "price": 129.99,
            "currency": "PLN",
            "isWishList": False,
            "imgUrl": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1465360/header.jpg?t=1782403733",
            "steamUrl": "https://store.steampowered.com/app/1465360/SnowRunner/"
            },
            {
            "appid": "g-1105",
            "title": "Cyberpunk 2077",
            "price": 199.9,
            "currency": "PLN",
            "isWishList": True,
            "imgUrl": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1465360/header.jpg?t=1782403733",
            "steamUrl": "https://store.steampowered.com/app/1465360/SnowRunner/"
            }
        ]
        }
        

