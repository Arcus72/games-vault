
def update_game_releases() -> None:
    import os
    import sys
    from pathlib import Path
    from sqlalchemy import func

    backend_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_dir))
    os.chdir(backend_dir)

    from database.database import SessionLocal
    from database.models import SteamGames
    from datetime import datetime, timedelta

    with SessionLocal.begin() as db:
        games_missing_release_date = db.query(SteamGames).filter(SteamGames.release_date == None).all()
        for game in games_missing_release_date:
            # tutaj dodać api do aktualizacji daty premiery
            print(1)

        recent_releases = db.query(SteamGames).filter(
            SteamGames.release_date != None,
            func.to_date(SteamGames.release_date, 'DD.MM.YYYY') >= (datetime.now() - timedelta(days=30)) # zastanowić się nad kolumną last_update 
        ).all()

        for game in recent_releases:
            # tutaj dodać api do aktualizacji rekomendacji i oceny metacritic
            print(1)

          
            db.add(game)

    print("Game releases update completed.")


