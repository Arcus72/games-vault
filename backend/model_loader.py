import time
from functools import lru_cache
from pathlib import Path

from config.settings import Settings
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import SentenceTransformer

settings = Settings()

MODEL_NAME = "BAAI/bge-m3"

@lru_cache(maxsize=1)
def get_llm_model() -> ChatGoogleGenerativeAI:
    """Zwraca instancję modelu LLM Google GenAI"""

    return ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", api_key=settings.GEMINI_API)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Zwraca instancję modelu embeddingów"""

    print("Ładowanie modelu BAAI/bge-m3 do pamięci...")
    model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)
    print("Model załadowany pomyślnie.")

    return model


def get_embedding(text: str) -> list[float]:
    """Generuje wektor embeddingów z podanego tekstu."""

    model = get_embedding_model()
    embedding = model.encode(text)

    return embedding.tolist()