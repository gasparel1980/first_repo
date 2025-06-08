
README - Magazin Mixt

Descriere proiect
Acest proiect este o aplicație simplă de gestionare a unui magazin, implementată în Python. Aplicația permite gestionarea produselor,
autentificarea și înregistrarea utilizatorilor (admin și client), efectuarea cumpărăturilor și exportul datelor în fișiere CSV.

Structura programului
- MagazinDB: Clasa responsabilă cu interacțiunea cu baza de date SQLite, gestionând tabelele pentru produse, utilizatori și istoricul cumpărăturilor.
- MagazinApp: Clasa care gestionează logica aplicației, meniurile pentru utilizatori (admin și client), validarea input-urilor și apelurile către MagazinDB.
- main.py: Scriptul principal care inițializează baza de date și pornește aplicația.

Funcționalități principale
- Crearea și autentificarea conturilor (admin/client) cu parole criptate SHA256.
- Adăugarea, editarea și ștergerea produselor (doar admin).
- Vizualizarea produselor și căutarea după nume sau categorie.
- Cumpărarea produselor cu verificarea stocului.
- Vizualizarea istoricului cumpărăturilor pentru fiecare client.
- Exportul produselor și istoricului în fișiere CSV.
- Raport zilnic al vânzărilor (doar admin).

Cerințe
- Python 3.x
- Biblioteca standard sqlite3 (inclusă în Python)
- Acces la sistemul de fișiere pentru salvarea bazelor de date și fișierelor CSV

Instrucțiuni de rulare
1. Asigură-te că ai Python 3 instalat.
2. Salvează toate fișierele programului în același folder.
3. Rulează scriptul principal:

python main.py

4. Urmează indicațiile din consolă pentru a crea un cont, autentifica sau utiliza aplicația.

Exemple din cod
Autentificare cu hash parolă (SHA256):

def hash_parola(self, parola):
    return hashlib.sha256(parola.encode()).hexdigest()

def autentificare(self, username, parola):
    parola_cr = self.hash_parola(parola)
    self.user_cursor.execute("SELECT id, rol FROM utilizatori WHERE username=? AND parola=?", (username, parola_cr))
    return self.user_cursor.fetchone()

Adăugare produs (admin):

def adauga_produs(self, categorie, nume, pret, stoc):
    self.cursor.execute("INSERT INTO produse (categorie, nume, pret, stoc) VALUES (?, ?, ?, ?)", (categorie, nume, pret, stoc))
    self.connection.commit()

Cumpărare produs:

def cumpara_produs(self, user_id, id_produs, cantitate):
    self.cursor.execute("SELECT categorie, nume, pret, stoc FROM produse WHERE id=?", (id_produs,))
    rezultat = self.cursor.fetchone()
    if not rezultat:
        return None
    categorie, nume, pret, stoc = rezultat
    if cantitate > 0 and stoc >= cantitate:
        total = pret * cantitate
        nou_stoc = stoc - cantitate
        self.cursor.execute("UPDATE produse SET stoc=? WHERE id=?", (nou_stoc, id_produs))
        data = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cursor.execute(
            "INSERT INTO istoric (user_id, categorie, produs, cantitate, total, data) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, categorie, nume, cantitate, total, data))
        self.connection.commit()
        return total, nume
    return None

Contact
Pentru întrebări sau sugestii, contactează: [Gășpărel Mihai - Adrian e-mail: gasparel_80@yahoo.com]
