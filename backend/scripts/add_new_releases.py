def clean_language(language: str) -> str:
    import re
    if not language:
        return ""

    language = re.sub(r"<[^>]+>", " ", language)
    language = re.sub(r"\[/?[^\]]+\]", "", language)
    language = re.sub(
        r"(?i)języki z pełnym udźwiękowieniem|\(full audio\)|\(text only\)|#lang_\w+",
        "",
        language
    )
    language = language.replace("\xa0", " ").replace("*", "").replace(";", "")
    language = re.sub(r"\s+", " ", language).strip()

    words = language.split(" ")
    return words[0] if words else ""

def add_new_releases(app_ids: list[int]) -> None:
    import requests
    from database.database import SessionLocal
    import json
    import sys
    from pathlib import Path

    backend_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_dir))

    from database.database import SessionLocal
    from database.models import SteamGames, Tags, Platforms, Languages
    from datetime import date, datetime

    PLATFORM_MAPPING = {
    "windows": "Windows",
    "mac": "Mac",
    "linux": "Linux",
    }

    POLISH_MONTHS = {
        "stycznia": 1,
        "lutego": 2,
        "marca": 3,
        "kwietnia": 4,
        "maja": 5,
        "czerwca": 6,
        "lipca": 7,
        "sierpnia": 8,
        "września": 9,
        "października": 10,
        "listopada": 11,
        "grudnia": 12
    }

    with SessionLocal.begin() as db:
        existing_games = db.query(SteamGames.appid).filter(SteamGames.appid.in_(app_ids)).all()
        not_existing_app_ids = set(app_ids) - {game.appid for game in existing_games}
        if not_existing_app_ids:
            for app_id in not_existing_app_ids:
                details_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=polish"
                response = requests.get(details_url) 

                if response.status_code == 200:
                    data = response.json()
                    game_data = data[str(app_id)]["data"]
                    release_date_str = game_data.get("release_date", {}).get("date", None)
                    release_date = release_date_str.split(" ")[0] + "." + str(POLISH_MONTHS.get(release_date_str.split(" ")[1], 1)) + "." + release_date_str.split(" ")[2] if release_date_str else None
                    release_date = datetime.strptime(release_date, "%d.%m.%Y").date() if release_date else None
                    is_released = (1 if game_data.get("release_date", {}).get("coming_soon", True) == False 
                        or game_data.get("release_date", {}).get("date", None) < datetime.now().date() 
                        else 0
                    ) 
                    pc_requirements = json.dumps(game_data.get("pc_requirements", {}), ensure_ascii=False) if game_data.get("pc_requirements") else None

                    new_game = SteamGames(
                        appid=app_id,
                        name=game_data.get("name"),
                        short_description=game_data.get("short_description"),
                        about_the_game=game_data.get("about_the_game"),
                        publisher=", ".join(game_data.get("publishers", [])),
                        developer=", ".join(game_data.get("developers", [])),
                        release_date=release_date,
                        is_released=is_released,
                        price=game_data.get("price_overview", {}).get("final", None) / 100 if game_data.get("price_overview") else 0,
                        website=game_data.get("website"),
                        pc_requirements=pc_requirements,
                        recommendations=game_data.get("recommendations", {}).get("total", None),
                        metacritic_score=game_data.get("metacritic", {}).get("score", None),
                        header_image_url=game_data.get("header_image"),
                        capsule_image_url=game_data.get("capsule_imagev5"),  
                        background_image_url=game_data.get("background"),  
                    )

                    platforms = game_data.get("platforms", {})
                    for platform, is_supported in platforms.items():
                        if is_supported and platform in PLATFORM_MAPPING:
                            platform_name = PLATFORM_MAPPING[platform]
                            platform_entry = db.query(Platforms).filter_by(platform=platform_name).first()
                            if platform_entry:
                                new_game.platforms.append(platform_entry)
                        
                    languages = game_data.get("supported_languages", "")
                    for language in languages.split(","):
                        cleaned_language = clean_language(language)
                        if cleaned_language:
                            language_entry = db.query(Languages).filter_by(language=cleaned_language).first()
                            if language_entry:
                                new_game.languages.append(language_entry)

                    tags = game_data.get("categories", [])
                    for tag in tags:
                        tag_name = tag.get("description")
                        if tag_name:
                            tag_entry = db.query(Tags).filter_by(tag=tag_name).first()
                            if tag_entry:
                                new_game.tags.append(tag_entry)

                    db.add(new_game)
                else:
                    print(f"Failed to fetch details for appid {app_id}.")
        else:
            print("All provided app_ids already exist in the database.")
            return
    print("New game releases added.")
    return
