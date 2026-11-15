import time
from functools import lru_cache
from pathlib import Path
from config.settings import Settings, get_settings
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import MinMaxScaler
import joblib

@lru_cache(maxsize=1)
def get_llm_model(settings: Settings = get_settings()) -> ChatGoogleGenerativeAI:
    """Zwraca instancję modelu LLM Google GenAI"""

    return ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", api_key=settings.GEMINI_API)

@lru_cache(maxsize=1)
def get_embedding_model(settings: Settings = get_settings()) -> SentenceTransformer:
    """Zwraca instancję modelu embeddingów"""

    print("Ładowanie modelu " + settings.MODEL_NAME + " do pamięci...")
    model = SentenceTransformer(settings.MODEL_NAME, token=settings.HF_TOKEN, trust_remote_code=True)
    print("Model załadowany pomyślnie.")

    return model

_ = get_embedding_model()  # Ładowanie do pamięci model embeddingów

def get_embedding(text: str) -> list[float]:
    """Generuje wektor embeddingów z podanego tekstu."""

    model = get_embedding_model()
    embedding = model.encode(text)

    return embedding.tolist()

@lru_cache(maxsize=1)
def get_als_artifacts() -> dict:
    """Zwraca zestaw artefaktów ALS (model, macierz, mapowania)."""

    return joblib.load("als_artifacts.joblib")

def get_als_recommendations(user_id: int, N: int = 100) -> list[int]:
    """Zwraca listę rekomendowanych ID gier dla danego użytkownika na podstawie modelu ALS."""

    artifacts = get_als_artifacts()
    
    model = artifacts["model"]
    user_item_matrix = artifacts["user_item_matrix"]
    user_to_index = artifacts["user_to_index"]
    index_to_app = artifacts["index_to_app"]

    # Jeśli użytkownika nie było w zbiorze treningowym, zwracamy pustą listę
    if user_id not in user_to_index:
        return []

    # Zamiana ID z bazy danych na indeks wiersza w macierzy
    target_idx = user_to_index[user_id]

    # Wygenerowanie rekomendacji
    ids, scores = model.recommend(
        userid=target_idx,
        user_items=user_item_matrix[target_idx],
        N=N,
        filter_already_liked_items=True,
    )

    if len(scores) == 0:
        return {}

    # Normalizacja Min-Max wyników do przedziału [0.0, 1.0]
    scaler = MinMaxScaler()
    norm_scores = scaler.fit_transform(scores.reshape(-1, 1)).flatten()

    # Zwracamy słownik {appid: znormalizowany_score}
    return {
        int(index_to_app[int(idx)]): float(score)
        for idx, score in zip(ids, norm_scores)
    }
