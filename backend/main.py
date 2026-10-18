import uuid
import hashlib
import base64
from bcrypt import checkpw
from fastapi import FastAPI, Depends, HTTPException, Request, Response, Body
from sqlalchemy import and_, func, nulls_last
from sqlalchemy.orm import Session
from database.database import get_db
from auth.user_auth import authenticate_session, create_new_session, authenticate_user, attach_user_to_session
from database.functions import gen_password_hash, get_filtered_steam_games, get_searched_games, filter_user_library, GamesPagination, GET_STEAM64, get_steam_library_games_list
from database.models import Users, UserSession, SteamGames, SteamLanguages, SteamGenres, SteamTags, SteamPlatforms, UserGameLibrary, Tags, Platforms, Genres, Languages
from fastapi.middleware.cors import CORSMiddleware
from schemas.schemas import GameFilter, GamesFilterRespone, UserCreate, UserLogin, GameSearchRespone, GameRespone, UserLibraryFilters, UserPasswordChange
from graph import chatbot_app
from langchain_core.messages import HumanMessage

app = FastAPI(
    
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

page_size = 30

# zostawiam w razie czego ale jest nie potrzebna bo każdy endpoint ma Depends(authenticate_session) ewentualnie można wrzucić przy wejściu na strone
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
                , "steam_id": user_session.user.steam_id
                , "session_id": user_session.session_id}
    return {"message": "Użytkownik nie jest zalogowany."}

@app.post("/api/create_user")
async def create_user(request: Request, data: UserCreate, session: UserSession = Depends(authenticate_session), db: Session = Depends(get_db)):
    username = data.username
    email = data.email
    password = data.password

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="Missing required fields.")

    existing_user = db.query(Users).filter((Users.username == username) | (Users.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Użytkownik o podanej nazwie użytkownika lub adresie e-mail już istnieje.")

    password_hash = gen_password_hash(password)
    new_user = Users(username=username, email=email, password_hash=password_hash, active=1)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Użytkownik utworzony pomyślnie. Teraz możesz się zalogować.", "user_id": new_user.id}

@app.post("/api/login")
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
        raise HTTPException(status_code=403, detail="Konto jest nieaktywne.")
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

@app.post("/api/change_password")
def change_password(data: UserPasswordChange, user_session: UserSession = Depends(authenticate_user), db: Session = Depends(get_db)):
    if not data.old_password or not data.new_password:
        raise HTTPException(status_code=400, detail="Brakujące wymagane pola.")

    user = db.query(Users).filter(Users.id == user_session.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie został znaleziony.")

    if not checkpw(data.old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Błędne stare hasło.")

    hashed_password = gen_password_hash(data.new_password)
    user.password_hash = hashed_password
    db.commit()

    return {"message": "Hasło zostało pomyślnie zmienione."}

@app.post("/api/add_steam_id")
def add_steam_id(steam_id: str, user_session: UserSession = Depends(authenticate_user), db: Session = Depends(get_db)):
    if not steam_id or user_session.user_id is None or 'https://steamcommunity.com/' not in steam_id:
        raise HTTPException(status_code=400, detail="Nieprawidłowy link do profilu Steam.")

    user = db.query(Users).filter(Users.id == user_session.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie został znaleziony.")
    user.steam_id = steam_id
    db.commit()
    return {"message": "Dodano Steam ID do profilu"}

@app.post("/api/get_steam_games", response_model=GamesFilterRespone)
def get_steam_games(filters: GameFilter, session: UserSession = Depends(authenticate_session), db: Session = Depends(get_db)) -> GamesFilterRespone:
    page = filters.page
    if not page or page < 1:
        page = 1
    query = get_filtered_steam_games(db, filters)
    if session.user_id is not None:
        query = query.outerjoin(
            UserGameLibrary,
            and_(
                UserGameLibrary.appid == SteamGames.appid,
                UserGameLibrary.user_id == session.user_id
            )
        ).add_entity(UserGameLibrary)
    games, total_pages = GamesPagination(query, page, page_size)
    if not games or total_pages == 0:
        raise HTTPException(status_code=404, detail="Nie znaleziono gier.")
    
    if session.user_id is not None:
            games_result = [
                GameRespone(
                    appid=game.appid,
                    name=game.name,
                    price=game.price,
                    release_date=game.release_date,
                    header_image=game.header_image_url,
                    status=lib.status if lib else 0,
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
                status=0,
            )
            for game in games
        ]

    return GamesFilterRespone(
        games=games_result,
        page=page,
        pages=total_pages,
    )

@app.post("/api/get_user_library", response_model=GamesFilterRespone)
def get_user_library(filters: UserLibraryFilters, db: Session = Depends(get_db), user_session: UserSession = Depends(authenticate_user)):
    page = filters.page
    if not page or page < 1:
        page = 1

    user_id = user_session.user.id
    query_user_library = filter_user_library(user_id, db, filters)
    user_library, total_pages = GamesPagination(query_user_library, page, page_size)
    if not user_library:
        raise HTTPException(status_code=404, detail="Nie znaleziono gier w bibliotece użytkownika.")

    library_result = [
        GameRespone(
            appid=game.appid,
            name=game.name,
            price=game.price,
            release_date=game.release_date,
            header_image=game.header_image_url,
            status=lib.status,
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
    searchbar_size = 6
    query = get_searched_games(db, filter)
    games = query.order_by(nulls_last(SteamGames.recommendations.desc())).limit(searchbar_size).all()

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


@app.post("/api/toggle_library_game")
def toggle_library_game(app_id: int = Body(embed=False), user_session: UserSession = Depends(authenticate_user), db: Session = Depends(get_db)):
    user_id = user_session.user_id
    if app_id and user_id:
        library = db.query(UserGameLibrary).filter(UserGameLibrary.user_id == user_id).filter(UserGameLibrary.appid == app_id).filter(UserGameLibrary.status == 2)
        wishlist = db.query(UserGameLibrary).filter(UserGameLibrary.user_id == user_id).filter(UserGameLibrary.appid == app_id).filter(UserGameLibrary.status == 1).first()
        if library.count() > 0:
            db.delete(library.first())
            db.commit()
            return {"status": 0, "message": "Usunięto z biblioteki"}
        elif wishlist:
            wishlist.status = 2
            db.commit()
            return {"status": 2, "message": "Dodano do biblioteki"}
        elif not wishlist and library.count() == 0:
            new_lib_game = UserGameLibrary(user_id=user_id,appid=app_id,status=2,FromSteam=0)
            db.add(new_lib_game)
            db.commit()
            db.refresh(new_lib_game)
            return {"status": 2, "message": "Dodano do biblioteki"}
        raise HTTPException(status_code=404, detail="Błąd przetawrzania")

# @app.post("/api/add_games_from_steam")
# def add_games_from_steam(user_session: UserSession = Depends(authenticate_user), db: Session = Depends(get_db)):
#     user_id = user_session.user_id
#     if user_id:
#         user = db.query(Users).filter(Users.id == user_id).first()
#         if not user or not user.steam_id:
#             raise HTTPException(status_code=404, detail="Nie znaleziono użytkownika lub brak Steam ID.")
        
#         steam_id64 = GET_STEAM64(user.steam_id)
#         games_list = get_steam_library_games_list(steam_id64)

#         query = db.query(UserGameLibrary).filter(UserGameLibrary.user_id == user_id).filter(UserGameLibrary.appid.in_(games_list)).all()

#         query_to_update = query.filter(UserGameLibrary.FromSteam == 0)

        
#         return {"message": steam_id64, "lista_gier": games_list}
#     raise HTTPException(status_code=404, detail="Błąd przetwarzania.")

@app.post("/api/toggle_wishlist_game")
def toggle_wishlist_game(app_id: int = Body(embed=False), user_session: UserSession = Depends(authenticate_user), db: Session = Depends(get_db)):
    user_id = user_session.user_id
    if app_id and user_id:
        wishlist = db.query(UserGameLibrary).filter(UserGameLibrary.user_id == user_id).filter(UserGameLibrary.appid == app_id).filter(UserGameLibrary.status == 1).first()
        library = db.query(UserGameLibrary).filter(UserGameLibrary.user_id == user_id).filter(UserGameLibrary.appid == app_id).filter(UserGameLibrary.status == 2).count()
        if library > 0:
            raise HTTPException(status_code=404, detail="Nie można dodać do listy życzeń gdy gra jest w bibliotece")
        elif wishlist:
            db.delete(wishlist)
            db.commit()
            return {"status": 0, "message": "Usunięto z listy życzeń"}
        elif library == 0 and not wishlist:
            new_wish_game = UserGameLibrary(user_id=user_id,appid=app_id,status=1,FromSteam=0)
            db.add(new_wish_game)
            db.commit()
            db.refresh(new_wish_game)
            return {"status": 1, "message": "Dodano do listy życzeń"}
        raise HTTPException(status_code=404, detail="Błąd przetawrzania")

@app.post("/api/toggle_hide_game")
def toggle_hide_game(app_id: int = Body(embed=False), user_session: UserSession = Depends(authenticate_user), db: Session = Depends(get_db)):
    user_id = user_session.user_id
    if app_id and user_id:
        lib = db.query(UserGameLibrary).filter(UserGameLibrary.user_id == user_id).filter(UserGameLibrary.appid == app_id).first()
        if lib and lib.status == 2:
            lib.status = 3
            db.commit()
            return {"status": 3, "message": "ukryto grę"}
        elif lib and lib.status == 3:
            lib.status = 2
            db.commit()
            return {"status": 2, "message": "odkryto grę"}
        elif lib and lib.status == 1:
            raise HTTPException(status_code=404, detail="Nie można ukryć gry, która jest na liście życzeń")
        elif not lib:
            raise HTTPException(status_code=404, detail="Nie można ukryć gry, która nie jest w bibliotece")
        raise HTTPException(status_code=404, detail="Błąd przetawrzania")

@app.post("/api/message")
async def get_message(
    data: dict,
    session: UserSession = Depends(authenticate_session),
    db: Session = Depends(get_db),
):
    user_message = data.get("question", "")

    config = {"configurable": {"thread_id": str(session.user_id)}}
    inputs = {"messages": [HumanMessage(content=user_message)]}

    result = await chatbot_app.ainvoke(inputs, config=config)

    bot_reply = result["messages"][-1].content[0]["text"]

    return {
        "success": True,
        "response": bot_reply,
        "games": [],
    }
