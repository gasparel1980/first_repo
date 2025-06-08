
import sqlite3

class MagazinApp:
    def __init__(self, db):
        self.db = db  # instanța bazei de date

    def citeste_float(self, mesaj):
        # Citește un număr float pozitiv de la utilizator, cu validare
        while True:
            try:
                valoare = float(input(mesaj))
                if valoare > 0:
                    return valoare
                else:
                    print(":( Introdu un număr pozitiv!")
            except ValueError:
                print(":( Introdu un număr valid!")

    def citeste_int(self, mesaj):
        # Citește un număr întreg pozitiv de la utilizator, cu validare
        while True:
            try:
                valoare = int(input(mesaj))
                if valoare > 0:
                    return valoare
                else:
                    print(":( Introdu un număr întreg pozitiv!")
            except ValueError:
                print(":( Introdu un număr întreg valid!")

    def meniu_principal(self):
        # Meniul principal care permite crearea contului, autentificarea sau ieșirea
        while True:
            print('*** MAGAZIN MIXT ***     (admin: Mihai pass: 123456 client: Simona pass: 123456')
            alegere = input("Ai cont? (da/nu  x - exit): ").lower()
            if alegere == "nu":
                self.creare_cont()
            elif alegere == "da":
                self.autentificare()
            elif alegere == 'x':
                self.iesire()
            else:
                print('Alegere incorectă!')

    def creare_cont(self):
        # Permite crearea unui cont nou (admin sau client)
        print('=== Creare cont ===')
        while True:
            username = input("Username: ")
            if len(username) < 3 or " " in username:
                print(":( Username-ul trebuie să aibă cel puțin 3 caractere și să nu conțină spații.")
            else:
                break
        while True:
            parola = input("Parola: ")
            if len(parola) < 5 or " " in parola:
                print(":( Parola trebuie să aibă cel puțin 5 caractere și să nu conțină spații.")
            else:
                break
        while True:
            rol = input("Rol (admin/client): ").lower()
            if rol == 'admin':
                # Protecție pentru crearea unui cont admin
                incercari = 3
                while incercari > 0:
                    print('Security code = admin2025')
                    cod = input('Security code: ')
                    if cod == 'admin2025':
                        try:
                            self.db.inregistrare_utilizator(username, parola, rol)
                            print(':) Admin creat cu succes!')
                        except sqlite3.IntegrityError:
                            print(':( Username deja existent.')
                        return
                    else:
                        incercari -= 1
                        print(f'Cod greșit! Încercări rămase: {incercari}')
                return
            elif rol == 'client':
                try:
                    self.db.inregistrare_utilizator(username, parola, rol)
                    print(':) Client creat cu succes!')
                except sqlite3.IntegrityError:
                    print(':( Username deja existent.')
                return
            else:
                print('Rol invalid!')

    def autentificare(self):
        # Permite autentificarea utilizatorului după username și parolă
        print('=== Autentificare ===')
        username = input("Username: ")
        parola = input("Parola: ")
        rezultat = self.db.autentificare(username, parola)
        if rezultat:
            user_id, rol = rezultat
            self.meniu_utilizator(user_id, username, rol)
        else:
            print(":( Autentificare eșuată.")

    def meniu_utilizator(self, user_id, username, rol):
        # Afișează meniul potrivit pentru rolul utilizatorului (admin sau client)
        if rol == "admin":
            self.meniu_admin(user_id, username)
        else:
            self.meniu_client(user_id, username)

    def meniu_admin(self, user_id, username):
        # Meniul pentru admin, cu opțiuni de administrare produse și rapoarte
        while True:
            print(
                f"\n[ADMIN - {username}] 1.Adaugă 2.Editează 3.Șterge 4.Produse 5.Export produse CSV 6.Raport vânzări/zi 7.Revenire 8.Ieșire")
            opt = input("Alege: ")

            if opt == "1":
                # Adaugă produs nou
                categorie = input("Categorie produs: ")
                nume = input("Nume produs: ")
                pret = self.citeste_float("Preț: ")
                stoc = self.citeste_int("Stoc: ")
                try:
                    self.db.adauga_produs(categorie, nume, pret, stoc)
                    print(":) Produs adăugat.")
                except:
                    print("! Produsul există deja.")
            elif opt == "2":
                # Editează produs existent
                idp = self.citeste_int("ID produs: ")
                categorie = input("Categorie noua: ")
                nume = input("Nume nou: ")
                pret = self.citeste_float("Preț nou: ")
                stoc = self.citeste_int("Stoc nou: ")
                rezultat = self.db.editeaza_produs(idp, categorie, nume, pret, stoc)
                if rezultat == "duplicate":
                    print(":( Există deja un produs cu acest nume!")
                elif rezultat:
                    print(":) Produs actualizat.")
                else:
                    print(":( ID invalid. Produsul nu a fost găsit.")
            elif opt == "3":
                # Șterge produs după nume
                nume = input("Nume produs de șters: ")
                deleted = self.db.sterge_produs(nume)
                if deleted:
                    print(":) Produs șters.")
                else:
                    print(":( Produsul nu există!")
            elif opt == "4":
                # Afișează toate produsele
                self.afiseaza_produse()
            elif opt == "5":
                # Exportă produsele în CSV
                self.db.export_produse_csv()
                print(":) Export realizat.")
            elif opt == "6":
                # Afișează raportul zilnic de vânzări
                self.afiseaza_vanzari_pe_zile()
            elif opt == "7":
                # Revine la meniul anterior
                return
            elif opt == "8":
                # Ieșire din aplicație
                self.iesire()

    def meniu_client(self, user_id, username):
        # Meniul pentru client, cu opțiuni de cumpărare și căutare produse
        while True:
            print(
                f"\n[CLIENT - {username}] 1.Cumpără 2.Caută produs 3.Caută categorie 4.Produse 5.Istoric 6.Export CSV 7.Revenire 8.Ieșire")
            opt = input("Alege: ")

            if opt == "1":
                # Cumpără produs
                idp = self.citeste_int("ID produs: ")
                cant = self.citeste_int("Cantitate: ")
                rezultat = self.db.cumpara_produs(user_id, idp, cant)
                if rezultat:
                    total, nume = rezultat
                    print(f":) Ai cumpărat {cant} buc. {nume} pentru {total:.2f} RON.")
                else:
                    print(":( Produs inexistent sau stoc insuficient.")
            elif opt == "2":
                # Caută produs după nume
                nume = input("Nume produs: ")
                produse = self.db.cauta_produs(nume)
                self.afiseaza_lista_produse(produse)
            elif opt == "3":
                # Caută produse după categorie
                categorie = input("Categorie: ")
                produse = self.db.cauta_dupa_categorie(categorie)
                self.afiseaza_lista_produse(produse)
            elif opt == "4":
                # Afișează toate produsele
                self.afiseaza_produse()
            elif opt == "5":
                # Afișează istoricul cumpărăturilor
                self.afiseaza_istoric(user_id, username)
            elif opt == "6":
                # Exportă istoricul în CSV
                self.db.export_istoric_csv(username, user_id)
                print(":) Export realizat.")
            elif opt == "7":
                # Revine la meniul principal
                return
            elif opt == "8":
                # Ieșire din aplicație
                self.iesire()

    def afiseaza_produse(self):
        # Afișează toate produsele
        produse = self.db.afiseaza_produse()
        self.afiseaza_lista_produse(produse)

    def afiseaza_lista_produse(self, produse):
        # Afișează o listă de produse
        if not produse:
            print(":( Nu există produse.")
            return
        print(f"\n{'ID':<3} {'Categorie':<10} {'Nume':<20} {'Preț':<7} {'Stoc':<5}")
        print("-" * 50)
        for p in produse:
            print(f"{p[0]:<3} {p[1]:<10} {p[2]:<20} {p[3]:<7.2f} {p[4]:<5}")

    def afiseaza_istoric(self, user_id, username):
        # Afișează istoricul cumpărăturilor pentru un utilizator
        istoric = self.db.istoric_cumparaturi(user_id)
        if not istoric:
            print(":( Nu există cumpărături în istoric.")
            return
        print(f"\nIstoric cumpărături pentru {username}:")
        print(f"{'Produs':<20} {'Cantitate':<9} {'Total':<7} {'Data':<16}")
        print("-" * 60)
        for prod, cant, total, data in istoric:
            print(f"{prod:<20} {cant:<9} {total:<7.2f} {data:<16}")

    def afiseaza_vanzari_pe_zile(self):
        # Afișează raportul zilnic cu total vânzări
        raport = self.db.vanzari_pe_zile()
        if not raport:
            print(":( Nu există vânzări.")
            return
        print("\nRaport vânzări pe zile:")
        print(f"{'Ziua':<12} {'Total vânzări':<15}")
        print("-" * 30)
        for zi, total in raport:
            print(f"{zi:<12} {total:<15.2f}")

    def iesire(self):
        # Închide conexiunile și oprește programul
        print("La revedere!")
        self.db.inchide()
        exit()