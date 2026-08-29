from schemas import AgentState


def recommendation_node(state: AgentState) -> AgentState:
    print("recommendation agent")
    return state