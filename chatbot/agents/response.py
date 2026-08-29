from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from model_loader import get_llm_model, load_df
from schemas import AgentState

response_system_prompt = SystemMessage(content="""
You format game search results into a user-friendly response.

Based on `message_intent`:
- **recommendation**: Suggest games with reasons, use enthusiastic tone
- **semantic_search**: List results with key details (title, price, genres, rating)

Rules:
- Use Markdown: **title** bold, • bullets
- Respond in Polish
- Keep it concise

CRITICAL RULE:
- ONLY mention games that are in the Results list below
- NEVER invent or suggest games not in the Results
- Don't apologize or offer alternatives outside the Results
""")

df = load_df()

def response_node(state: AgentState) -> AgentState:
    print("response agent")

    model = get_llm_model()

    # TAKI TROCHĘ RAG. TRZEBA PRZEKAZAĆ INFROMACJE O GRACH Z BAZY DO LLM
    # Filter the DataFrame to only include games present in the results 
    df_subset = df[df['name'].isin([result['name'] for result in state['results']])]
    results_text = "\n".join([f"{row['name']} - {row['about_the_game']} - {row['short_description']} - {row['developers']}" for _, row in df_subset.iterrows()])

    messages = [
        SystemMessage(content=response_system_prompt.content),
        HumanMessage(content=f"User: {state['messages'][-1].content}\nResults: {results_text}")
    ]

    formatted_response = model.invoke(messages)
    
    return {"messages": [AIMessage(content=formatted_response.content)]}