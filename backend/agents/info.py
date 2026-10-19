from rapidfuzz import process, fuzz
from database.database import get_db
from database.models import SteamGames
from schemas.agent_schemas import AgentState

# Próg podobieństwa tekstowego (0 - 100)
FUZZY_SCORE_THRESHOLD = 75.0


def info_node(state: AgentState) -> dict:
    print("info agent")

    # Pobranie nazwy gry ze stanu
    active_game = state.get("active_game")

    if not active_game:
        print("Brak 'active_game' w stanie.")
        return {"results": []}

    query_text = active_game.strip()
    db = next(get_db())

    try:
        # Pobranie z bazy danych aktualnej listy par (nazwa, appid)
        games_from_db = (
            db.query(SteamGames.name, SteamGames.appid)
            .filter(SteamGames.name.is_not(None))
            .all()
        )

        if not games_from_db:
            print("Baza danych nie zwróciła żadnych gier.")
            return {"results": []}

        # Przygotowanie słownika do dopasowania {nazwa_gry: appid}
        games_dict = {name: appid for name, appid in games_from_db}

        # Wyszukiwanie rozmyte (Fuzzy Matching) przy użyciu RapidFuzz
        match = process.extractOne(
            query_text,
            choices=games_dict.keys(),
            scorer=fuzz.WRatio,  # Zbalansowany algorytm pod kątem literówek i wielkości liter
        )

        if match:
            best_title, score, _ = match
            print(
                f"RapidFuzz dopasował: '{best_title}' (Podobieństwo: {score:.1f}%)"
            )

            # Weryfikacja progu pewności
            if score >= FUZZY_SCORE_THRESHOLD:
                matched_id = games_dict[best_title]
                print(f"Trafienie: {best_title} (appid: {matched_id})")
                return {"results": [matched_id]}
            else:
                print(
                    f"Najlepsze dopasowanie '{best_title}' ma zbyt niski wynik ({score:.1f}% < {FUZZY_SCORE_THRESHOLD}%)."
                )

        print(f"Nie znaleziono w bazie gry pasującej do: '{query_text}'")
        return {"results": []}

    except Exception as e:
        print(f"Błąd w info_node: {e}")
        return {"results": []}
    finally:
        db.close()