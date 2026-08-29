from model_loader import get_embedding_model, load_df, load_embeddings, load_hnsw_index

from schemas import AgentState

df = load_df()
embedding_model = get_embedding_model()
embeddings = load_embeddings()
index = load_hnsw_index()

def semantic_search_node(state: AgentState) -> AgentState:
    print("semantic search agent")

    embedded_text = embedding_model.encode(state["messages"][-1].content)
    labels, distances = index.knn_query(embedded_text, k = 3)

    print("Wyniki:")
    for label, distance in zip(labels[0], distances[0]):
        app_data = df.iloc[label]
        print(f" - {app_data['name']} (Odległość: {distance:.4f})")

    return {"results": [{"name": df.iloc[label]["name"], "distance": float(distance)} for label, distance in zip(labels[0], distances[0])]}