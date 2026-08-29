import time
from functools import lru_cache
from pathlib import Path

import hnswlib
import numpy as np
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import SentenceTransformer

from settings import api_key


@lru_cache(maxsize=1)
def get_llm_model() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite", 
        api_key=api_key
    )


MODEL_CACHE_DIR = Path.home() / ".cache" / "sentence_transformers"
MODEL_PATH = MODEL_CACHE_DIR / "BAAI_bge-m3"

def get_embedding_model():
    print("Ładowanie modelu embeddingów...")
    start = time.time()
    
    if MODEL_PATH.exists():
        print(f"Ładowanie z cache: {MODEL_PATH}")
        model = SentenceTransformer(str(MODEL_PATH))
    else:
        print("Pobieranie modelu (pierwsze uruchomienie)...")
        model = SentenceTransformer("BAAI/bge-m3", trust_remote_code=True)
        print("Zapisywanie do cache...")
        model.save(str(MODEL_PATH))
    
    print(f"Model załadowany w {time.time() - start:.2f}s")
    return model


@lru_cache(maxsize=1)
def load_embeddings(data_path: str = "games-vault/chatbot/data/embeddings.npy") -> np.ndarray:
    return np.load(data_path)


@lru_cache(maxsize=1)
def load_df(data_path: str = "games-vault/chatbot/data/steam_app_details.jsonl") -> pd.DataFrame:
    return pd.read_json(data_path, lines=True, nrows=1000)  # Limit to 10,000 rows for performance


@lru_cache(maxsize=1)
def load_hnsw_index(data_path: str = "games-vault/chatbot/data/hnsw_index.bin") -> hnswlib.Index:
    embeddings = load_embeddings()
    index = hnswlib.Index(space='cosine', dim=embeddings.shape[1])
    index.load_index(data_path, embeddings.shape[1])
    return index