# Visitor Counter

Prosta aplikacja Flask + PostgreSQL, która zlicza wizyty na stronie i wyświetla komunikat:

> **„Cześć! Jesteś N. osobą odwiedzającą tę stronę."**

## Stack

- **Python 3.13 + Flask** – backend
- **PostgreSQL 16** – baza danych (tabela `visits`)
- **Gunicorn** – WSGI server produkcyjny
- **Docker + Docker Compose** – konteneryzacja
- **Traefik labels** – integracja z reverse proxy Coolify

---

## Szybki start lokalny

```bash
# 1. Sklonuj repo
git clone <URL_REPO>
cd visitor-counter

# 2. Skopiuj zmienne środowiskowe
cp .env.example .env
# Edytuj .env i ustaw hasło do bazy

# 3. Uruchom
docker compose up --build

# 4. Otwórz http://localhost:8000
```

---

## Wdrożenie przez Coolify

### 1. Utwórz nowy projekt w Coolify

1. W panelu Coolify → **New Resource** → **Docker Compose**
2. Wskaż repozytorium GitHub (lub wklej URL)
3. Ustaw **Build Pack**: `Docker Compose`
4. Plik Compose: `docker-compose.yml`

### 2. Zmienne środowiskowe w Coolify

W zakładce **Environment Variables** dodaj:

| Zmienna           | Wartość przykładowa          |
|-------------------|------------------------------|
| `POSTGRES_USER`   | `postgres`                   |
| `POSTGRES_PASSWORD` | `silne_haslo_tu`           |
| `POSTGRES_DB`     | `visitordb`                  |
| `APP_DOMAIN`      | `visitor.twoja-domena.pl`    |

### 3. Deploy

Kliknij **Deploy** – Coolify:
- zbuduje obraz Dockera z `Dockerfile`
- uruchomi kontener PostgreSQL
- uruchomi aplikację (z healthcheckiem)
- skonfiguruje Traefik + SSL (Let's Encrypt)

### 4. Auto-deploy (CI/CD)

W Coolify włącz **"Deploy on push"** dla gałęzi `main`.
Każdy push do repozytorium GitHub automatycznie wyzwoli nowy deploy.

---

## Endpointy

| Endpoint  | Opis                                     |
|-----------|------------------------------------------|
| `GET /`   | Strona główna – liczy wizytę i wyświetla |
| `GET /health` | Health check (status bazy danych)   |

---

## Schemat bazy danych

```sql
CREATE TABLE visits (
    id         SERIAL PRIMARY KEY,
    visited_at TIMESTAMP DEFAULT NOW()
);
```

Każde odwiedzenie strony `GET /` dodaje jeden rekord do tabeli `visits`.

---

## Monitoring

Aplikacja loguje do `stdout`/`stderr` (standardowy Docker logging).
Loki + Grafana z Coolify podbiją logi automatycznie.

Health check (`/health`) zwraca:
```json
{"status": "ok", "db": "connected"}
```
