# Trabalho_BD

## Database Relationships

The project includes relationships between:

* **Artists ↔ Songs**
* **Users ↔ Playlists**
* **Songs ↔ Playlists** (many-to-many through `musica_playlist`)

---

## Database Structure

```mermaid
erDiagram

    ARTISTA {
        INT id PK
        VARCHAR nome UK
        VARCHAR nacionalidade
    }

    MUSICA {
        INT id PK
        VARCHAR titulo
        INT duracao_segundos
        INT artista_id FK
    }

    USUARIO {
        INT id PK
        VARCHAR username UK
        VARCHAR email UK
    }

    PLAYLIST {
        INT playlist_id PK
        INT usuario_id PK, FK
        VARCHAR nome
        DATETIME data_criacao
    }

    MUSICA_PLAYLIST {
        INT musica_id PK, FK
        INT playlist_id PK, FK
        INT usuario_id PK, FK
        INT ordem_na_playlist
    }

    ARTISTA ||--o{ MUSICA : possui

    USUARIO ||--o{ PLAYLIST : cria

    PLAYLIST ||--o{ MUSICA_PLAYLIST : contem

    MUSICA ||--o{ MUSICA_PLAYLIST : participa
```

### Entity Mapping

#### Strong Entities

**ARTISTA**
- Primary Key: `id`
- Constraints:
  - `nome` → UNIQUE, NOT NULL

**USUARIO**
- Primary Key: `id`
- Constraints:
  - `username` → UNIQUE, NOT NULL
  - `email` → UNIQUE, NOT NULL

**MUSICA**
- Primary Key: `id`
- Foreign Key:
  - `artista_id → artista.id`
- Constraints:
  - `titulo` → NOT NULL
  - `duracao_segundos > 0` (CHECK)

#### Weak Entity

**PLAYLIST**
- Composite Primary Key:
  - `playlist_id`
  - `usuario_id`
- Foreign Key:
  - `usuario_id → usuario.id`
- Relationship:
  - One user can own multiple playlists (1:N)

#### Many-to-Many Relationship

**MUSICA_PLAYLIST**
- Junction table between `MUSICA` and `PLAYLIST`
- Composite Primary Key:
  - `musica_id`
  - `playlist_id`
  - `usuario_id`
- Stores:
  - Song position inside playlist (`ordem_na_playlist`)

### Relationship Summary

| Relationship | Type |
|-------------|------|
| ARTISTA → MUSICA | 1:N |
| USUARIO → PLAYLIST | 1:N |
| MUSICA → PLAYLIST | N:N |
| PLAYLIST → MUSICA_PLAYLIST | 1:N |
| MUSICA → MUSICA_PLAYLIST | 1:N |

A REST API built with Flask, SQLAlchemy, and PostgreSQL for managing artists, songs, playlists, and users. This project was developed as a database-oriented application, providing CRUD operations and relationships between musical entities.

## Features

* Artist management
* Music management
* Playlist management
* User management
* Relational database support with PostgreSQL
* Database migrations using Flask-Migrate / Alembic
* Modular route organization using Flask Blueprints

## Tech Stack

* **Python 3**
* **Flask**
* **Flask-SQLAlchemy**
* **Flask-Migrate**
* **SQLAlchemy**
* **PostgreSQL**
* **Docker Compose**
* **Alembic**

## Project Structure

```text
trabalho_BD/
│── app.py
│── config.py
│── extensions.py
│── requirements.txt
│── docker-compose.yml
│── LICENSE
│
├── models/
│   ├── artista.py
│   ├── musica.py
│   ├── playlist.py
│   ├── usuario.py
│   └── musica_playlist.py
│
├── routes/
│   ├── artista_routes.py
│   ├── musica_routes.py
│   ├── playlist_routes.py
│   └── usuario_routes.py
│
├── migrations/
└── venv/
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd trabalho_BD
```

### 2. Create and activate a virtual environment

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root and configure your database connection:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
FLASK_APP=app.py
FLASK_ENV=development
```

Make sure your `config.py` reads environment variables correctly.

## Database Setup

### Run database migrations

Initialize migrations (if necessary):

```bash
flask db init
```

Generate a migration:

```bash
flask db migrate -m "Initial migration"
```

Apply migrations:

```bash
flask db upgrade
```

## Running the Application

Start the Flask server:

```bash
python app.py
```

The application will run at:

```text
http://127.0.0.1:5000
```

## API Routes

The API is organized into the following modules:

| Entity    | Route Module         |
| --------- | -------------------- |
| Artists   | `artista_routes.py`  |
| Songs     | `musica_routes.py`   |
| Users     | `usuario_routes.py`  |
| Playlists | `playlist_routes.py` |

Available endpoints depend on the CRUD implementation inside each route file.

Example:

```http
GET /artistas
POST /musicas
PUT /playlists/<id>
DELETE /usuarios/<id>
```

## Database Relationships

The project includes relationships between:

* **Artists ↔ Songs**
* **Users ↔ Playlists**
* **Songs ↔ Playlists** (many-to-many through `musica_playlist`)

## Docker

If `docker-compose.yml` is configured, start services with:

```bash
docker compose up --build
```

Or:

```bash
docker-compose up --build
```

## Dependencies

Main libraries used:

* Flask
* Flask-SQLAlchemy
* Flask-Migrate
* SQLAlchemy
* psycopg2-binary
* python-dotenv

## License

This project is distributed under the terms of the LICENSE file included in the repository.
