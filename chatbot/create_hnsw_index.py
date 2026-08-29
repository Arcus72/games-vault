# Algorytm, który przyśpiesza wyszukiwanie najbliższych sąsiadów w dużych zbiorach danych wektorowych.
# Jak będziemy mieli dane w bazie, to będzie to wbudowane w rozszerzenie PostgreSQL - pgvector
import hnswlib
import numpy as np

# Load embeddings from file
embeddings = np.load(f"embeddings.npy")

# Create HNSW index
index = hnswlib.Index(space='cosine', dim=embeddings.shape[1])
index.load_index("hnsw_index.bin", embeddings.shape[1])
index.init_index(max_elements=len(embeddings), ef_construction=200, M=16)
index.add_items(embeddings)
index.save_index("hnsw_index.bin")