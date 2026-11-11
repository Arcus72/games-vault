from database.database import get_db
from model_loader import get_embedding_model
from database.models import SteamGames


def add_embeddings(batch_size: int = 4):
    db = next(get_db())
    embedding_model = get_embedding_model()

    try:
        # Pobieramy tylko rekordy, które nie mają jeszcze wygenerowanego wektora
        games = db.query(SteamGames).filter(SteamGames.embedding.is_(None)).all()
        total_games = len(games)
        print(f"Znaleziono {total_games} gier bez embeddingu.")

        for i in range(0, total_games, batch_size):
            batch = games[i : i + batch_size]

            # 1. Tworzenie pełnego tekstu opisowego dla każdej gry z paczki
            doc_texts = []
            for game in batch:
                short_desc = (game.short_description or "").strip()
                about_game = (game.about_the_game or "").strip()

                # Nagłówek podstawowych informacji
                text_parts = [
                    f"Tytuł: {game.name}",
                    f"Deweloper: {game.developer or ''}",
                    f"Wydawca: {game.publisher or ''}",
                ]

                # Jeśli opisy są identyczne lub jeden z nich jest pusty, dodajemy tylko jeden
                if short_desc == about_game or not about_game:
                    if short_desc:
                        text_parts.append(f"Opis: {short_desc}")
                else:
                    if short_desc:
                        text_parts.append(f"Opis: {short_desc}")
                    if about_game:
                        text_parts.append(f"O grze: {about_game}")

                full_text = "\n".join(text_parts)
                doc_texts.append(full_text)

            # 2. Wygenerowanie wektorów w jednej paczce (Batching)
            vectors = embedding_model.encode(doc_texts)

            # 3. Przypisanie wektorów do obiektów ORM
            for game, vector in zip(batch, vectors):
                game.embedding = (
                    vector.tolist() if hasattr(vector, "tolist") else vector
                )

            # 4. Zapis do bazy
            db.commit()
            print(
                f"Zapisano {min(i + batch_size, total_games)} / {total_games} gier"
            )

        print("Proces generowania embeddingów zakończony sukcesem!")

    except Exception as e:
        db.rollback()
        print(f"Błąd podczas generowania embeddingów: {e}")
    finally:
        db.close()
