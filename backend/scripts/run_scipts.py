from cleanup_expired_records import cleanup_expired_records
from add_new_releases import add_new_releases
from find_new_releases import get_top_upcoming_steam_ids
from add_embeddings import add_embeddings

if __name__ == "__main__":

    app_list = get_top_upcoming_steam_ids()

    cleanup_expired_records()
    add_new_releases(app_list)
    add_embeddings()