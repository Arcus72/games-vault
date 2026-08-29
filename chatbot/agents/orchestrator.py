from langchain_core.messages import HumanMessage, SystemMessage

from model_loader import get_llm_model
from schemas import AgentState, IntentClassifier

orchestrator_system_prompt = SystemMessage(content = """
You are the Coordinator Agent of a Multi-Agent System for Steam games.

# INTENT CLASSIFICATION
Classify user intent into EXACTLY ONE of these categories:

1. "recommendation" - User wants game recommendations
   Examples: "Recommend games like Elden Ring", "What should I play?", "Suggest co-op games"

2. "semantic_search" - User describes game features or asks about specific games
   Examples: "Survival game with crafting", "Game where you build a castle"

# EXTRACTION RULES
For "recommendation" or "semantic_search":
- Extract filters: genres, platforms, max_price, min_price, min_rating, release_after, language
- Extract reference game if mentioned

Examples:
User: "Recommend games like Elden Ring cheaper than 200 PLN"
→ intent: "recommendation", filters: {"max_price": 200}, reference: "Elden Ring"

User: "Survival game with base building"
→ intent: "semantic_search"
""")

def orchestrator_node(state: AgentState):
    model = get_llm_model()
    structured_llm = model.with_structured_output(IntentClassifier)

    messages = [
        SystemMessage(content=orchestrator_system_prompt.content),
        HumanMessage(content=state["messages"][-1].content)
    ]

    result = structured_llm.invoke(messages)
    print(f"📝 Intent: {result.message_intent}")
    if result.filters:
        print(f"🔍 Filtry: {result.filters}")

    return {"message_intent": result.message_intent}