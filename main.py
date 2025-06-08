
from db import MagazinDB
from app import MagazinApp

if __name__ == "__main__":
    # Creăm o instanță a clasei MagazinDB (interfața cu baza de date)
    db = MagazinDB()
    # Creăm o instanță a clasei MagazinApp cu db ca parametru
    app = MagazinApp(db)
    # Pornim meniul principal al aplicației
    app.meniu_principal()