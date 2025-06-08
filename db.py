
import sqlite3
import hashlib
import datetime
import csv

class MagazinDB:
    def __init__(self, db_name="magazin.db", user_db_name="utilizatori.db"):
        # Conectare de baza de date pentru produse si creare db_name daca nu exista
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        # Conectare la baza de date pentru utilizatori si creare user_db_name daca nu exista
        self.user_connection = sqlite3.connect(user_db_name)
        self.user_cursor = self.user_connection.cursor()
        # Creare tabele dacă nu există
        self.creaza_tabele()

    def creaza_tabele(self):
        # Creare tabel produse
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS produse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categorie TEXT,
                nume TEXT UNIQUE,
                pret REAL,
                stoc INTEGER
            )
        """)
        # Creare tabel istoric cumpărături
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS istoric (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                categorie TEXT,
                produs TEXT,
                cantitate INTEGER,
                total REAL,
                data TEXT
            )
        """)
        self.connection.commit()
        # Creare tabel utilizatori
        self.user_cursor.execute("""
            CREATE TABLE IF NOT EXISTS utilizatori (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                parola TEXT,
                rol TEXT
            )
        """)
        self.user_connection.commit()

    def hash_parola(self, parola):
        # Criptare parola folosind SHA256
        return hashlib.sha256(parola.encode()).hexdigest()

    def autentificare(self, username, parola):
        # Verifică dacă username și parola (criptata) există în baza de date
        parola_cr = self.hash_parola(parola)
        self.user_cursor.execute("SELECT id, rol FROM utilizatori WHERE username=? AND parola=?", (username, parola_cr))
        return self.user_cursor.fetchone()  # Returnează tuplu (id, rol) sau None

    def inregistrare_utilizator(self, username, parola, rol):
        # Înregistrează un utilizator nou cu username, parola (criptata) și rol
        parola_cr = self.hash_parola(parola)
        self.user_cursor.execute("INSERT INTO utilizatori (username, parola, rol) VALUES (?, ?, ?)", (username, parola_cr, rol))
        self.user_connection.commit()

    def adauga_produs(self, categorie, nume, pret, stoc):
        # Adaugă un produs nou în tabelul produse
        self.cursor.execute("INSERT INTO produse (categorie, nume, pret, stoc) VALUES (?, ?, ?, ?)", (categorie, nume, pret, stoc))
        self.connection.commit()

    def editeaza_produs(self, id_produs, categorie_noua, nume_nou, pret_nou, stoc_nou):
        # Editează un produs după ID, returnează True dacă a fost modificat, "duplicate" dacă numele există deja
        try:
            self.cursor.execute("UPDATE produse SET categorie=?, nume=?, pret=?, stoc=? WHERE id=?", (categorie_noua, nume_nou, pret_nou, stoc_nou, id_produs))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return "duplicate"

    def sterge_produs(self, nume_produs):
        # Șterge produs după nume, returnează True dacă produsul a fost șters
        self.cursor.execute("DELETE FROM produse WHERE nume=?", (nume_produs,))
        self.connection.commit()
        return self.cursor.rowcount > 0

    def afiseaza_produse(self):
        # Returnează toate produsele ordonate alfabetic după categorie și nume
        self.cursor.execute("SELECT * FROM produse ORDER BY categorie ASC, nume ASC")
        return self.cursor.fetchall()

    def cauta_produs(self, nume):
        # Caută produse după nume (partial, case insensitive)
        self.cursor.execute("SELECT * FROM produse WHERE LOWER(nume) LIKE ?", (f"%{nume.lower()}%",))
        return self.cursor.fetchall()

    def cauta_dupa_categorie(self, categorie):
        # Caută produse după categorie (partial, case insensitive)
        self.cursor.execute("SELECT * FROM produse WHERE LOWER(categorie) LIKE ?", (f"%{categorie.lower()}%",))
        return self.cursor.fetchall()

    def cumpara_produs(self, user_id, id_produs, cantitate):
        # Permite cumpărarea unui produs dacă există stoc suficient
        self.cursor.execute("SELECT categorie, nume, pret, stoc FROM produse WHERE id=?", (id_produs,))
        rezultat = self.cursor.fetchone()
        if not rezultat:
            return None  # Produs inexistent

        categorie, nume, pret, stoc = rezultat
        if cantitate > 0 and stoc >= cantitate:
            total = pret * cantitate
            nou_stoc = stoc - cantitate
            # Actualizează stocul
            self.cursor.execute("UPDATE produse SET stoc=? WHERE id=?", (nou_stoc, id_produs))
            # Adaugă în istoricul cumpărăturilor
            data = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.cursor.execute(
                "INSERT INTO istoric (user_id, categorie, produs, cantitate, total, data) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, categorie, nume, cantitate, total, data))
            self.connection.commit()
            return total, nume

        return None  # Stoc insuficient sau cantitate invalidă

    def istoric_cumparaturi(self, user_id):
        # Returnează istoricul cumpărăturilor unui utilizator
        self.cursor.execute("SELECT produs, cantitate, total, data FROM istoric WHERE user_id=?", (user_id,))
        return self.cursor.fetchall()

    def vanzari_pe_zile(self):
        # Returnează totalul vânzărilor grupate pe zile
        self.cursor.execute("""
            SELECT DATE(data) as ziua, SUM(total) as total_zi 
            FROM istoric 
            GROUP BY ziua 
            ORDER BY ziua ASC
        """)
        return self.cursor.fetchall()

    def export_produse_csv(self):
        # Exportă lista de produse într-un fișier CSV
        produse = self.afiseaza_produse()
        with open("produse.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Categorie", "Nume", "Preț", "Stoc"])
            writer.writerows(produse)

    def export_istoric_csv(self, username, user_id):
        # Exportă istoricul cumpărăturilor unui utilizator într-un fișier CSV
        istoric = self.istoric_cumparaturi(user_id)
        with open(f'{username}.csv', "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Categorie", "Produs", "Cantitate", "Total", "Data"])
            writer.writerows(istoric)

    def inchide(self):
        # Închide conexiunile și cursorii bazelor de date
        self.cursor.close()
        self.connection.close()
        self.user_cursor.close()
        self.user_connection.close()

