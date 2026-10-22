from langchain_core.tools import tool
import requests

from database.models import SteamGames, Genres, Languages, Tags, Platforms


def apply_filters(query, filters: dict):
    """Aplikuje filtry użytkownika do zapytania SQLAlchemy."""
    if not filters:
        return query

    for filter_name, value in filters.items():
        if value is None or value == "" or value == []:
            continue

        # Filtry ceny
        if filter_name == "price_max":
            query = query.filter(SteamGames.price <= value)

        # Filtry premier
        elif filter_name == "IsReleased":
            if value is True:
                query = query.filter(
                    SteamGames.release_date.isnot(None), SteamGames.release_date != ""
                )
            elif value is False:
                query = query.filter(
                    (SteamGames.release_date.is_(None))
                    | (SteamGames.release_date == "")
                )

        # Filtry dat
        elif filter_name == "release_date_min_year":
            query = query.filter(SteamGames.release_date >= value)
        elif filter_name == "release_date_max_year":
            query = query.filter(SteamGames.release_date <= value)

        # Filtry gatunków
        elif filter_name == "genres":
            for genre_name in value:
                query = query.filter(SteamGames.genres.any(Genres.genre.ilike(f"%{genre_name}%")))

        # Filtry języków
        elif filter_name == "languages":
            for lang_name in value:
                query = query.filter(SteamGames.languages.any(Languages.language.ilike(f"%{lang_name}%")))

        # Filtry tagów
        elif filter_name == "tags":
            for tag_name in value:
                query = query.filter(SteamGames.tags.any(Tags.tag.ilike(f"%{tag_name}%")))

        # Filtry platform
        elif filter_name == "platforms":
            for platform_name in value:
                query = query.filter(SteamGames.platforms.any(Platforms.platform.ilike(f"%{platform_name}%")))

    return query


@tool
def currency_converter_to_PLN(amount, from_currency):
    """
    Converts an amount from one currency to PLN using a fixed exchange rate.
    
    Args:
        amount (float): The amount of money to convert.
        from_currency (str): The currency code of the original currency (e.g., 'USD').
    """

    from_currency = from_currency.upper()
    url = "https://api.nbp.pl/api/exchangerates/tables/A/?format=json"

    try:
        response = requests.get(url)
        response.raise_for_status() 

        data = response.json()

        exchange_rate = None
        for rate in data[0]['rates']:
            if rate['code'] == from_currency:
                exchange_rate = rate['mid']
                break

        if exchange_rate is None:
            print(f"Nie znaleziono kursu wymiany dla waluty: {from_currency}")
            return None

        # Convert the amount
        converted_amount = amount * exchange_rate
        print(f"{amount} {from_currency} = {converted_amount:.2f} PLN")

        return converted_amount

    except requests.RequestException as e:
        print(f"Błąd podczas pobierania kursu wymiany: {e}")
        return None
