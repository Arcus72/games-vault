from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import html
from bs4 import BeautifulSoup

df = pd.read_json("games-vault/chatbot/data/steam_app_details.jsonl", lines=True, nrows=1000)

COLUMNS = [
    "name",
    "genres",
    "categories",
    "short_description",
    "about_the_game",
    "content_descriptors",
]

FIELD_NAMES = {
    "name": "Nazwa gry",
    "genres": "Gatunki",
    "categories": "Kategorie",
    "short_description": "Krótki opis",
    "about_the_game": "Opis gry",
    "content_descriptors": "Informacje o zawartości",
}

# WYGENEROWANE SZYBKIE CZYSZCZENIE TEKSTU DO TESTÓW (DO ZMIANY)
def clean_text(value):
    """Czyści tekst, HTML i niepotrzebne białe znaki."""

    if value is None:
        return ""

    # Zamiana encji HTML, np. &nbsp; -> spacja
    value = html.unescape(str(value))

    # Usunięcie tagów HTML
    value = BeautifulSoup(value, "html.parser").get_text(" ", strip=True)

    # Czyszczenie białych znaków
    value = value.replace("\xa0", " ")
    value = " ".join(value.split())

    return value.strip()


def format_value(value, column=None):

    if value is None:
        return ""

    if isinstance(value, float) and pd.isna(value):
        return ""

    # numpy array -> list
    if isinstance(value, np.ndarray):
        value = value.tolist()

    # Lista
    if isinstance(value, list):

        formatted = []

        for item in value:

            # np.:
            # {"id": 1, "description": "Akcja"}
            if isinstance(item, dict):

                if "description" in item:
                    description = clean_text(item["description"])

                    if description:
                        formatted.append(description)

                elif "notes" in item:
                    notes = clean_text(item["notes"])

                    if notes:
                        formatted.append(notes)

            else:
                item = clean_text(item)

                if item:
                    formatted.append(item)

        return ", ".join(formatted)

    # Dict
    if isinstance(value, dict):

        # genres / categories
        if "description" in value:
            return clean_text(value["description"])

        # content_descriptors
        if "notes" in value:
            return clean_text(value["notes"])

        # Awaryjnie dla innych dictów
        formatted = []

        for key, val in value.items():

            if val not in [None, "", [], {}]:
                formatted.append(
                    f"{key}: {clean_text(val)}"
                )

        return ", ".join(formatted)

    # Zwykły tekst
    return clean_text(value)


def create_embedding_text(row):

    text = []
    seen_values = set()

    for col in COLUMNS:

        if col not in row:
            continue

        value = format_value(row[col], col)

        if not value:
            continue

        # Nie powtarzaj identycznego tekstu
        if value in seen_values:
            continue

        seen_values.add(value)

        field_name = FIELD_NAMES.get(col, col)

        text.append(
            f"{field_name}: {value}"
        )

    return "\n".join(text)


df["embedding_text"] = df.apply(
    create_embedding_text,
    axis=1
)

texts = df["embedding_text"].tolist()

model = SentenceTransformer(
    "BAAI/bge-m3",
    trust_remote_code=True,
)

embeddings = model.encode(texts, show_progress_bar=True)
np.save("embeddings.npy", embeddings)