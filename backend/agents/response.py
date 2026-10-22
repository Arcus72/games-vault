from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from model_loader import get_llm_model
from schemas.agent_schemas import AgentState
from sqlalchemy.orm import selectinload
from database.database import get_db
from database.models import SteamGames

response_system_prompt = SystemMessage(content="""
You format game search results into a user-friendly response.

Based on `message_intent`:
- **recommendation**: Suggest games with reasons, use enthusiastic tone
- **semantic_search**: List results with key details (title, price, genres, rating)
- **game_info**: Provide a comprehensive overview of the requested game

Rules:
- Use Markdown: **title** bold, • bullets
- Respond in Polish
- Keep it concise

CRITICAL RULE:
- ONLY mention games that are in the Results list below
- NEVER invent or suggest games not in the Results
- Don't apologize or offer alternatives outside the Results
""")


def response_node(state: AgentState) -> dict:
    print("response agent")
    intent = state.get("message_intent")
    results = state.get("results", [])

    # Jeśli brak wyników dla wyszukiwania i rekomendacji
    if intent in ("semantic_search", "recommendation") and not results:
        msg = (
            "Niestety nie znalazłem żadnych gier pasujących do Twojego zapytania."
            if intent == "semantic_search"
            else "Niestety nie znalazłem żadnych rekomendacji gier dopasowanych do Twojego profilu i filtrów."
        )
        return {
            "messages": [AIMessage(content=[{"type": "text", "text": msg}])],
            "games": [],
        }

    db = next(get_db())
    try:

        # Pobranie danych z bazy
        matched_games = (
            db.query(SteamGames)
            .options(
                selectinload(SteamGames.genres),
                selectinload(SteamGames.platforms),
                selectinload(SteamGames.languages),
                selectinload(SteamGames.tags),
            )
            .filter(SteamGames.appid.in_(results))
            .all()
        )

        if not matched_games:
            msg = "Nie znaleziono szczegółów dotyczących wybranych gier."
            return {
                "messages": [AIMessage(content=[{"type": "text", "text": msg}])],
                "games": [],
            }

        # Budowanie kontekstu dla LLM zależnie od intencji
        if intent == "game_info":
            game = matched_games[0]

            # Formatowanie relacji many-to-many do czytelnych ciągów tekstowych
            genres_str = ", ".join([g.genre for g in game.genres]) if game.genres else "Brak"
            platforms_str = ", ".join([p.platform for p in game.platforms]) if game.platforms else "Brak"
            languages_str = ", ".join([l.language for l in game.languages]) if game.languages else "Brak"
            tags_str = ", ".join([t.tag for t in game.tags]) if game.tags else "Brak"

            context_str = (
                f"Tytuł: {game.name}\n"
                f"Krótki opis: {game.short_description or 'Brak'}\n"
                f"O grze: {game.about_the_game or 'Brak'}\n"
                f"Wydawca: {game.publisher or 'Brak'}\n"
                f"Deweloper: {game.developer or 'Brak'}\n"
                f"Data premiery: {game.release_date or 'Brak'}\n"
                f"Ocena Metacritic: {game.metacritic_score or 'Brak'}\n"
                f"Wymagania PC: {game.pc_requirements or 'Brak'}\n"
                f"Cena: {game.price}\n"
                f"Gatunki: {genres_str}\n"
                f"Platformy: {platforms_str}\n"
                f"Języki: {languages_str}\n"
                f"Tagi: {tags_str}\n"
            )
            instructions = "Odpowiadaj na pytania użytkownika WYŁĄCZNIE na podstawie poniższych informacji z bazy danych:"

        elif intent == "semantic_search":
            context_str = "\n".join(
                [
                    f"--- ZNALEZIONA GRA ---\n"
                    f"Tytuł: {g.name or 'Brak'}\n"
                    f"Opis: {g.short_description or 'Brak'}\n"
                    f"O grze: {g.about_the_game or 'Brak'}\n"
                    f"Wydawca: {g.publisher or 'Brak'}\n"
                    f"Data premiery: {g.release_date or 'Brak'}\n"
                    f"Cena: {g.price or 'Brak'}\n"
                    f"Gatunki: {', '.join([genre.genre for genre in g.genres]) if g.genres else 'Brak'}\n"
                    for g in matched_games
                ]
            )
            instructions = (
                "Na podstawie poniższych informacji z bazy danych przedstaw użytkownikowi wszystkie "
                "podane gry i krótko wyjaśnij, dlaczego do niego pasują.\n"
                "Odpowiadaj WYŁĄCZNIE na podstawie poniższego kontekstu:"
            )

        elif intent == "recommendation":
            context_str = "\n".join(
                [
                    f"--- DEDYKOWANA REKOMENDACJA ---\n"
                    f"Tytuł: {g.name or 'Brak'}\n"
                    f"Opis: {g.short_description or 'Brak'}\n"
                    f"O grze: {g.about_the_game or 'Brak'}\n"
                    f"Wydawca: {g.publisher or 'Brak'}\n"
                    f"Data premiery: {g.release_date or 'Brak'}\n"
                    f"Cena: {g.price or 'Brak'}\n"
                    f"Gatunki: {', '.join([genre.genre for genre in g.genres]) if g.genres else 'Brak'}\n"
                    for g in matched_games
                ]
            )
            instructions = (
                "Na podstawie analizy preferencji oraz biblioteki użytkownika dobrano dla niego poniższe propozycje gier.\n"
                "Przedstaw te rekomendacje w atrakcyjny sposób, wyjaśniając, dlaczego te pozycje są warte uwagi.\n"
                "Odpowiadaj WYŁĄCZNIE na podstawie poniższego kontekstu z bazy danych:"
            )
        else:
            return {
                "messages": [AIMessage(content=[{"type": "text", "text": "Nieznana intencja wiadomości."}])]
            }

        # Generowanie odpowiedzi przez LLM
        system_prompt = SystemMessage(
            content=f"Jesteś ekspertowym doradcą i asystentem gier wideo. {instructions}\n\nKONTEKST:\n{context_str}"
        )
        messages = [system_prompt, HumanMessage(content=state["messages"][-1].content)]

        response = get_llm_model().invoke(messages)

        # Wyciągnięcie tekstu do printa/debugowania
        content_text = (
            response.content[0]["text"]
            if isinstance(response.content, list)
            else response.content
        )

        print("\n\nRESPONSE AGENT OUTPUT:\n")
        print(content_text)
        print("\n--------------------\n")

        return {
            "messages": [AIMessage(content=response.content)],
            "games": [
                {
                    "id": g.appid,
                    "title": g.name,
                    "price": g.price,
                    "currency": "PLN",
                    "isWishList": False,
                    "imgUrl": g.header_image_url,
                    "steamUrl": g.background_image_url,
                }
                for g in matched_games
            ],
        }

    finally:
        db.close()