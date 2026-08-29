import uuid

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agents import tools
from agents.orchestrator import orchestrator_node
from agents.recommendation import recommendation_node
from agents.semantic_search import semantic_search_node
from agents.response import response_node
from schemas import AgentState

graph = StateGraph(AgentState)

# tool_node = ToolNode(tools=tools)

graph.add_node("orchestrator", orchestrator_node)
graph.add_node("recommendation_agent", recommendation_node)
graph.add_node("semantic_search_agent", semantic_search_node)
graph.add_node("response_agent", response_node)
# graph.add_node("chat_agent", chat_agent_node)

graph.add_edge(START, 'orchestrator')

graph.add_conditional_edges(
    'orchestrator', 
    lambda state: state['message_intent'],
    {
        'recommendation': 'recommendation_agent',
        'semantic_search': 'semantic_search_agent',
        # 'chat': 'chat_agent'
    }
)

graph.add_edge('recommendation_agent', 'response_agent')
graph.add_edge('semantic_search_agent', 'response_agent')
graph.add_edge('response_agent', END)

checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)

config = {'configurable': {'thread_id': uuid.uuid4()}}


while True:
    user_message = input('Enter message:')
    result = app.invoke({'messages': [{'role': 'user', 'content': user_message}]}, config=config)
    print(result['messages'][-1].content)