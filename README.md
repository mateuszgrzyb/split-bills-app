Rachunko

Aplikacja do wspólnego ewidencjonowania wydatków i rozliczania ich w grupie.

Technologie

Frontend: HTML, CSS i JavaScript

Backend: Python i FastAPI

Baza danych: PostgreSQL

ORM: SQLAlchemy

Aktualny stan

Backend udostępnia stronę informacyjną oraz GET /api/health.

Modele bazy obejmują użytkowników, grupy, uczestników i rachunki.

Tabele można utworzyć w PostgreSQL na podstawie modeli.

Frontend jest demonstracyjnym widokiem z przykładowymi danymi.

Formularz wydatku działa tylko w przeglądarce — dane nie są jeszcze zapisywane przez API.

Endpointy CRUD dla grup i rachunków są do przygotowania.

Struktura projektu

Rachunko/
├── backend/
│   ├── app/
│   │   ├── api/routes/health.py
│   │   ├── create_tables.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── models.py
│   └── requirements.txt
└── frontend/
    ├── css/
    ├── js/
    └── index.html

Uruchomienie lokalne (Windows)

Wymagania

Python

PostgreSQL

pgAdmin lub inne narzędzie do zarządzania PostgreSQL

1. Utwórz bazę PostgreSQL

Uruchom usługę PostgreSQL. Jeśli baza rachunko jeszcze nie istnieje, otwórz w pgAdmin Query Tool połączony z bazą postgres i wykonaj:

CREATE DATABASE rachunko;

To polecenie tworzy bazę. Tabele zostaną utworzone w kolejnym kroku na podstawie modeli SQLAlchemy.

2. Przygotuj backend

W terminalu PowerShell, z katalogu głównego repozytorium:

Set-Location .\backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt

Utwórz plik backend/.env i wpisz adres połączenia:

DATABASE_URL=postgresql+psycopg://postgres:TWOJE_HASLO@localhost:5432/rachunko

Zastąp TWOJE_HASLO hasłem użytkownika PostgreSQL. Jeśli używasz innego użytkownika, hosta lub portu, zmień odpowiednie wartości. Nie dodawaj pliku .env do repozytorium.

3. Utwórz tabele

Będąc w katalogu backend, uruchom:

.\.venv\Scripts\python.exe -m app.create_tables

Polecenie utworzy brakujące tabele. Nie zmienia kolumn w tabelach, które już istnieją.

4. Uruchom API

W tym samym terminalu, nadal z katalogu backend, uruchom:

.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

API będzie dostępne pod http://127.0.0.1:8000.

Dokumentacja API: http://127.0.0.1:8000/docs

Status API: http://127.0.0.1:8000/api/health

5. Uruchom frontend

Zostaw API działające. Otwórz drugi terminal w katalogu głównym projektu i uruchom:

py -m http.server 5500 --directory frontend

Otwórz http://127.0.0.1:5500 w przeglądarce. Frontend sprawdza status API, ale nadal pokazuje przykładowe dane. Formularz nie zapisuje wydatków w bazie.

Uwagi

Dane dostępowe do PostgreSQL przechowuj lokalnie w backend/.env.

Po zmianie modeli ponowne uruchomienie create_tables nie zaktualizuje istniejących kolumn.

