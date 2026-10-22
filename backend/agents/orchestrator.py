from langchain_core.messages import HumanMessage, SystemMessage

from model_loader import get_llm_model
from schemas.agent_schemas import AgentState, IntentClassifier
from database.database import get_db
from database.models import Genres, Languages, Platforms, Tags


def orchestrator_node(state: AgentState):
    model = get_llm_model()
    structured_llm = model.with_structured_output(IntentClassifier)

    orchestrator_system_prompt = get_orchestrator_prompt()

    messages = [
        SystemMessage(content=orchestrator_system_prompt.content),
        HumanMessage(content=state["messages"][-1].content),
    ]

    result = structured_llm.invoke(messages)
    print(f"📝 Intent: {result.message_intent}")
    if result.filters:
        print(f"🔍 Filtry: {result.filters}")
    print(f"🎯 Active game: {result.active_game}")

    return {
        "message_intent": result.message_intent,
        "filters": result.filters.model_dump() if result.filters else {},
        "active_game": (
            result.active_game if result.active_game else state.get("active_game")
        ),
    }


def get_orchestrator_prompt() -> SystemMessage:
    db = next(get_db())
    try:
        # Pobieramy unikalne wartości z bazy
        available_genres = [g.genre for g in db.query(Genres.genre).all()]
        available_platforms = [p.platform for p in db.query(Platforms.platform).all()]
        available_languages = [l.language for l in db.query(Languages.language).all()]

        # Jeśli tagów jest bardzo dużo (np. tysiące), pobieramy np. TOP 100 najpopularniejszych
        available_tags = [t.tag for t in db.query(Tags.tag).limit(100).all()]
    finally:
        db.close()

    content = f"""
Jesteś Agentem Koordynatorem (Coordinator Agent) systemu wieloagentowego dedykowanego grom na platformie Steam.

# JĘZYK KOMUNIKACJI I ODPOCZYNKU
- ZAWSZE przetwarzaj dane i odpowiadaj WYŁĄCZNIE w języku polskim.
- Niezależnie od języka, w którym użytkownik zada pytanie, wszystkie analizy, wyjściowe struktury danych i komunikaty musisz tworzyć po polsku.

# KLASYFIKACJA INTENCJI (INTENT CLASSIFICATION)
Sklasyfikuj intencję użytkownika do DOKŁADNIE JEDNEJ z poniższych kategorii:

1. "recommendation" – Użytkownik szuka rekomendacji gier.
   Przykłady: "Poleć mi gry podobne do Elden Ring", "W co powinienem zagrać?", "Zasugeruj gry w trybie kooperacji"

2. "semantic_search" – Użytkownik opisuje cechy gry lub szuka gier po mechanikach/motywach.
   Przykłady: "Gra survivalowa z tworzeniem przedmiotów", "Gra, w której buduje się zamek"

3. "game_info" – Użytkownik pyta o szczegółowe informacje, opisy lub dane dotyczące jednej konkretnej gry.
   Przykłady: "Powiedz mi wszystko o Cyberpunk 2077", "Jaka jest cena Witcher 3?", "Opowiedz mi o grze GTA V"

# ZASADY EKSTRAKCJI DANYCH (EXTRACTION RULES)
- Dla intencji "game_info": Wyodrębnij nazwę docelowej gry do pola `active_game`.
- Dla intencji "recommendation": Wyodrębnij grę odniesienia (jeśli została wspomniana) do pola `active_game` oraz wszelkie filtry.
- Dla intencji "semantic_search": Wyodrębnij filtry (gatunki, platformy, max_price itp.).

Przykłady:
Użytkownik: "Poleć gry podobne do Elden Ring tańsze niż 200 PLN"
→ intent: "recommendation", filters: dict("max_price": 200), reference: "Elden Ring"

Użytkownik: "Gra survivalowa z rozbudową bazy"
→ intent: "semantic_search"

# DOZWOLONE WARTOŚCI FILTRÓW (ALLOWED FILTER VALUES)
Wszystkie dopasowane filtry MUSZĄ dokładnie odpowiadać wartościom z poniższych list:

- **DOZWOLONE GATUNKI (genres)**: {available_genres}
- **DOZWOLONE PLATFORMY (platforms)**: {available_platforms}
- **DOZWOLONE JĘZYKI (languages)**: {available_languages}
- **DOZWOLONE TAGI (tags)**: {available_tags}

ZASADA MAPOWANIA: Jeśli użytkownik użyje odmiany słowa (np. "gry strategiczne"), ZAWSZE zamień ją na dokładny odpowiednik z powyższych list (np. "strategie").

Filtry wyciągaj tylko i wyłącznie z tego co napisze użytkownik.
"""
    return SystemMessage(content=content)
