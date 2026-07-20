# Games Vault API — run with: uvicorn main:app --port 4000
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import json 

app = FastAPI(title="Games Vault API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

PAGE_SIZE = 10

@app.post("/api/games")
def get_games(data: dict = Body(default={})):
    print("Request data:", data)
    with open("games.json", "r") as f:
        GAMES = json.load(f)

    pagination = data.get("pagination", data)
    total_pages = max(1, -(-len(GAMES) // PAGE_SIZE))
    page = max(1, min(int(pagination.get("currentPage") or 1), total_pages))
    start = (page - 1) * PAGE_SIZE

    return {
        "success": True,
        "games": GAMES[start:start + PAGE_SIZE],
        "currentPage": page,
        "totalPages": total_pages,

    }

@app.post("/api/library")
def get_games(data: dict = Body(default={})):
    print("Request data:", data)
    with open("games.json", "r") as f:
        GAMES = json.load(f)

    pagination = data.get("pagination", data)
    total_pages = max(1, -(-len(GAMES) // PAGE_SIZE))
    page = max(1, min(int(pagination.get("currentPage") or 1), total_pages))
    start = (page - 1) * PAGE_SIZE

    return {
        "success": True,
        "games": GAMES[start:start + PAGE_SIZE],
        "currentPage": page,
        "totalPages": total_pages,

    }


@app.post("/api/message")
def get_message(data: dict = Body(default={})):
    user_message = data.get("question", "")
    print("User message:", user_message)
    return {
        "success": True,
        "response": "This is the list of games that will suit you best:",
        "games": [
            {
            "id": "g-9842",
            "title": "The Witcher 3: Wild Hunt",
            "price": 129.99,
            "currency": "PLN",
            "isWishList": False,
            "imgUrl": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1465360/header.jpg?t=1782403733",
            "steamUrl": "https://store.steampowered.com/app/1465360/SnowRunner/"
            },
            {
            "id": "g-1105",
            "title": "Cyberpunk 2077",
            "price": 199.9,
            "currency": "PLN",
            "isWishList": True,
            "imgUrl": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1465360/header.jpg?t=1782403733",
            "steamUrl": "https://store.steampowered.com/app/1465360/SnowRunner/"
            }
        ]
        }
