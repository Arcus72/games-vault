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

    db = next(get_db())

    # INFO AGENT RESPONSE
    if state.get("message_intent") == "game_info":

        game = (
            db.query(SteamGames.short_description, SteamGames.about_the_game, SteamGames.publisher, SteamGames.release_date, SteamGames.price, SteamGames.pc_requirements)
            .filter(SteamGames.appid == state.get("results")[0]["id"])
            .first()
        )

        context_str = f"""
            Tytuł/Opis: {game.short_description}
            Wydawca: {game.publisher}
            Data premiery: {game.release_date}
            Cena: {game.price}
            Wymagania PC: {game.pc_requirements}
            O grze: {game.about_the_game}
        """

        system_prompt = SystemMessage(
            content=f"Jesteś pomocnym asystentem gier wideo. Odpowiadaj na pytania użytkownika WYŁĄCZNIE na podstawie poniższych informacji z bazy danych:\n\nKONTEKST:\n{context_str}"
        )

        messages = [
            SystemMessage(content=system_prompt.content),
            HumanMessage(content=state["messages"][-1].content)
        ]

        model = get_llm_model()
        response = model.invoke(messages)

        print("\n\nRESPONSE AGENT OUTPUT:\n")
        print(response.content[0]["text"])
        print("\n--------------------\n")
        return {
            "messages": [AIMessage(content=response.content)],
            "active_game": state.get("results")[0]["name"],
        }

    # SEMANTIC SEARCH RESPONSE
    if state.get("message_intent") == "semantic_search":

        results = state.get("results", [])

        if not results:
            return {
                "messages": [
                    AIMessage(
                        content="Niestety nie znalazłem żadnych gier pasujących do Twojego zapytania."
                    )
                ]
            }

        # Pobieramy ID wszystkich znalezionych gier z wyników wyszukiwania semantycznego
        appids = [game["id"] for game in results]

        # Pobieramy szczegółowe informacje z bazy danych dla znalezionych gier
        matched_games = (
            db.query(
                SteamGames.appid,
                SteamGames.name,
                SteamGames.short_description,
                SteamGames.publisher,
                SteamGames.price,
                SteamGames.release_date,
            )
            .filter(SteamGames.appid.in_(appids))
            .all()
        )

        # Budujemy wzbogacony kontekst dla każdego zebranego rekordu (RAG)
        context_blocks = []
        for g in matched_games:
            block = (
                f"--- GAME --- \n"
                f"Tytuł: {g.name}\n"
                f"Wydawca: {g.publisher}\n"
                f"Data premiery: {g.release_date}\n"
                f"Cena: {g.price}\n"
                f"Opis: {g.short_description}\n"
            )
            context_blocks.append(block)

        context_str = "\n".join(context_blocks)

        # Promp systemu nakazujący odpowiadanie WYŁĄCZNIE na podstawie zebranego kontekstu
        system_prompt = SystemMessage(
            content=(
                "Jesteś pomocnym asystentem gier wideo. Na podstawie poniższych informacji z bazy danych "
                "przedstaw użytkownikowi wszystkie podane gry i krótko wyjaśnij, dlaczego do niego pasują.\n"
                "Odpowiadaj WYŁĄCZNIE na podstawie poniższego kontekstu:\n\n"
                f"KONTEKST:\n{context_str}"
            )
        )

        messages = [system_prompt, HumanMessage(content=state["messages"][-1].content)]

        model = get_llm_model()
        response = model.invoke(messages)

        # Wyciągnięcie tekstu z odpowiedzi (dostosowane do struktury LangChain / Anthropic / OpenAI)
        content_text = (
            response.content[0]["text"]
            if isinstance(response.content, list)
            else response.content
        )

        print("\n\nRESPONSE AGENT OUTPUT:\n")
        print(content_text)
        print("\n--------------------\n")

        return {"messages": [AIMessage(content=response.content)]}

    # RECOMMENDATION AGENT RESPONSE
    if state.get("message_intent") == "recommendation":

        results = state.get("results", [])

        if not results:
            return {
                "messages": [
                    AIMessage(
                        content="Niestety nie znalazłem żadnych rekomendacji gier dopasowanych do Twojego profilu i filtrow."
                    )
                ]
            }

        # Pobieramy ID wszystkich poleconych gier
        appids = [game["id"] for game in results]

        # Pobieramy szczegółowe informacje z bazy danych dla znalezionych gier
        matched_games = (
            db.query(
                SteamGames.appid,
                SteamGames.name,
                SteamGames.short_description,
                SteamGames.publisher,
                SteamGames.price,
                SteamGames.release_date,
            )
            .filter(SteamGames.appid.in_(appids))
            .all()
        )

        # Budujemy wzbogacony kontekst RAG
        context_blocks = []
        for g in matched_games:
            block = (
                f"--- DEDYKOWANA REKOMENDACJA --- \n"
                f"Tytuł: {g.name}\n"
                f"Wydawca: {g.publisher}\n"
                f"Data premiery: {g.release_date}\n"
                f"Cena: {g.price}\n"
                f"Opis: {g.short_description}\n"
            )
            context_blocks.append(block)

        context_str = "\n".join(context_blocks)

        system_prompt = SystemMessage(
            content=(
                "Jesteś ekspertowym doradcą i asystentem gier wideo. Na podstawie analizy preferencji oraz "
                "biblioteki użytkownika dobrano dla niego poniższe propozycje gier.\n"
                "Przedstaw te rekomendacje w atrakcyjny sposób, wyjaśniając, dlaczego te pozycje są warte uwagi.\n"
                "Odpowiadaj WYŁĄCZNIE na podstawie ponizszego kontekstu z bazy danych:\n\n"
                f"KONTEKST REKOMENDACJI:\n{context_str}"
            )
        )

        messages = [system_prompt, HumanMessage(content=state["messages"][-1].content)]

        model = get_llm_model()
        response = model.invoke(messages)

        # Bezpieczne wyciągnięcie tekstu z odpowiedzi
        content_text = (
            response.content[0]["text"]
            if isinstance(response.content, list)
            else response.content
        )

        print("\n\nRESPONSE AGENT OUTPUT:\n")
        print(content_text)
        print("\n--------------------\n")

        # Zwracamy AIMessage ze spreparowanym tekstem content_text
        return {"messages": [AIMessage(content=response.content)]}
