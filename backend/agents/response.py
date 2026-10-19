from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from model_loader import get_llm_model
from schemas.agent_schemas import AgentState
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
        return {"messages": [AIMessage(content=msg)]}

    db = next(get_db())
    try:

        # Pobranie danych z bazy
        matched_games = (
            db.query(
                SteamGames.appid,
                SteamGames.name,
                SteamGames.short_description,
                SteamGames.about_the_game,
                SteamGames.publisher,
                SteamGames.price,
                SteamGames.release_date,
                SteamGames.pc_requirements,
                SteamGames.header_image_url,
                SteamGames.background_image_url,
            )
            .filter(SteamGames.appid.in_(results))
            .all()
        )

        if not matched_games:
            return {
                "messages": [
                    AIMessage(
                        content="Nie znaleziono szczegółów dotyczących wybranych gier."
                    )
                ]
            }

        # Budowanie kontekstu dla LLM zależnie od intencji
        if intent == "game_info":
            game = matched_games[0]
            context_str = (
                f"Tytuł/Opis: {game.short_description}\n"
                f"Wydawca: {game.publisher}\n"
                f"Data premiery: {game.release_date}\n"
                f"Cena: {game.price}\n"
                f"Wymagania PC: {game.pc_requirements}\n"
                f"O grze: {game.about_the_game}"
            )
            instructions = "Odpowiadaj na pytania użytkownika WYŁĄCZNIE na podstawie poniższych informacji z bazy danych:"

        elif intent == "semantic_search":
            context_str = "\n".join(
                [
                    f"--- GAME ---\nTytuł: {g.name}\nWydawca: {g.publisher}\n"
                    f"Data premiery: {g.release_date}\nCena: {g.price}\nOpis: {g.short_description}\n"
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
                    f"--- DEDYKOWANA REKOMENDACJA ---\nTytuł: {g.name}\nWydawca: {g.publisher}\n"
                    f"Data premiery: {g.release_date}\nCena: {g.price}\nOpis: {g.short_description}\n"
                    for g in matched_games
                ]
            )
            instructions = (
                "Na podstawie analizy preferencji oraz biblioteki użytkownika dobrano dla niego poniższe propozycje gier.\n"
                "Przedstaw te rekomendacje w atrakcyjny sposób, wyjaśniając, dlaczego te pozycje są warte uwagi.\n"
                "Odpowiadaj WYŁĄCZNIE na podstawie poniższego kontekstu z bazy danych:"
            )
        else:
            return {"messages": [AIMessage(content="Nieznana intencja wiadomości.")]}

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