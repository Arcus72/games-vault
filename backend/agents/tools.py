from langchain_core.tools import tool
import requests


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
