# Rachunko

Lekki szkielet aplikacji do dzielenia wydatków w grupie. Backend jest oparty na FastAPI, a frontend to responsywny HTML, CSS i JavaScript bez dodatkowego bundlera.

## Struktura

```text
rachunko-starter/
├── backend/
│   ├── app/
│   │   ├── api/routes/health.py
│   │   └── main.py
│   └── requirements.txt
└── frontend/
    ├── css/styles.css
    ├── js/api.js
    ├── js/app.js
    └── index.html
```

## Uruchomienie na Windows

### 1. Backend

W pierwszym terminalu:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

API będzie dostępne pod `http://127.0.0.1:8000`, a interaktywna dokumentacja Swagger pod `http://127.0.0.1:8000/docs`.

### 2. Frontend

W drugim terminalu, z katalogu `rachunko-starter`:

```powershell
py -m http.server 5500 --directory frontend
```

Otwórz `http://127.0.0.1:5500`. Frontend sprawdzi połączenie z API i pokaże jego status.

## Co już jest

- działający punkt kontrolny `GET /api/health`;
- konfiguracja CORS dla lokalnego frontendu;
- responsywny ekran grupy z przykładowymi danymi;
- formularz demonstracyjny dodawania wydatku działający w przeglądarce;
- osobny moduł klienta API, gotowy do rozbudowy.

Wydatki widoczne w tej makiecie są przykładowe. Formularz działa wyłącznie lokalnie w przeglądarce i jeszcze nie zapisuje danych na backendzie. To celowy punkt startowy: kolejnym krokiem będzie ustalenie modeli danych i dodanie bazy oraz endpointów grup, uczestników, wydatków i rozliczeń.

## Ustawienie adresu API

Domyślnie frontend łączy się z `http://127.0.0.1:8000`. Adres można zmienić w `frontend/js/api.js`.
