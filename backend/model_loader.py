import time
from functools import lru_cache
from pathlib import Path
from config.settings import Settings, get_settings
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import SentenceTransformer

@lru_cache(maxsize=1)
def get_llm_model(settings: Settings = get_settings()) -> ChatGoogleGenerativeAI:
    """Zwraca instancję modelu LLM Google GenAI"""

    return ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", api_key=settings.GEMINI_API)

@lru_cache(maxsize=1)
def get_embedding_model(settings: Settings = get_settings()) -> SentenceTransformer:
    """Zwraca instancję modelu embeddingów"""

    print("Ładowanie modelu " + settings.MODEL_NAME + " do pamięci...")
    model = SentenceTransformer(settings.MODEL_NAME, trust_remote_code=True)
    print("Model załadowany pomyślnie.")

    return model

_ = get_embedding_model()  # Ładowanie do pamięci model embeddingów

def get_embedding(text: str) -> list[float]:
    """Generuje wektor embeddingów z podanego tekstu."""

    model = get_embedding_model()
    embedding = model.encode(text)

    return embedding.tolist()