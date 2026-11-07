from cleanup_expired_records import cleanup_expired_records
from add_new_releases import add_new_releases

if __name__ == "__main__":

    app_list = [4115450] # tu dodać wywołanie funkcji co uzupełni app_liste

    cleanup_expired_records()
    add_new_releases(app_list)