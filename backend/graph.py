from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from agents.orchestrator import orchestrator_node
from agents.recommendation import recommendation_node
from agents.semantic_search import semantic_search_node
from agents.info import info_node
from agents.response import response_node
from schemas.agent_schemas import AgentState


def build_app():
    graph = StateGraph(AgentState)

    # tool_node = ToolNode(tools=tools)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("recommendation_agent", recommendation_node)
    graph.add_node("semantic_search_agent", semantic_search_node)
    graph.add_node("info_agent", info_node)
    graph.add_node("response_agent", response_node)

    graph.add_edge(START, 'orchestrator')

    graph.add_conditional_edges(
        'orchestrator', 
        lambda state: state['message_intent'],
        {
            'recommendation': 'recommendation_agent',
            'semantic_search': 'semantic_search_agent',
            'game_info': 'info_agent'
        }
    )

    graph.add_edge('recommendation_agent', 'response_agent')
    graph.add_edge('semantic_search_agent', 'response_agent')
    graph.add_edge('info_agent', 'response_agent')
    graph.add_edge('response_agent', END)

    checkpointer = InMemorySaver()
    app = graph.compile(checkpointer=checkpointer)

    return app

# Tworzymy pojedynczą instancję aplikacji
chatbot_app = build_app()
