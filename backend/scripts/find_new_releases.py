import requests
from bs4 import BeautifulSoup


def get_top_upcoming_steam_ids(limit: int = 20) -> list[str]:
    """Zwraca listę ID (AppID) dla najpopularniejszych nadchodzących gier ze Steam."""
    url = (
        "https://store.steampowered.com/search/results/"
        "?query&start=0&count=100&filter=popularcomingsoon&infinite=1"
    )
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    html_content = response.json().get("results_html", "")
    soup = BeautifulSoup(html_content, "html.parser")

    app_ids = []
    for row in soup.find_all("a", class_="search_result_row"):
        raw_appid = row.get("data-ds-appid")
        if not raw_appid:
            continue

        # W przypadku zestawów/DLC wybieramy główny AppID
        app_id = raw_appid.split(",")[0]

        if app_id not in app_ids:
            app_ids.append(app_id)

        if len(app_ids) >= limit:
            break

    return app_ids
