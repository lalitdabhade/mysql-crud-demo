# MySQL CRUD Tasks API

A small FastAPI REST API for managing tasks in a local MySQL database. SQL is plain and uses PyMySQL parameterized queries; no ORM is used.

## Prerequisites

- Python 3.10 or newer
- A running local MySQL server
- A MySQL user and database created for this application

## Setup

### Windows PowerShell

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Copy the environment template and fill in the local credentials:

```powershell
Copy-Item .env.example .env
```

Set `DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` in `.env`. Do not commit `.env`.

4. Create the database if needed. The API can create the `tasks` table, but the database itself must already exist:

```sql
CREATE DATABASE your_database_name;
```

## Run

```powershell
uvicorn app.main:app --reload
```

Open the interactive API documentation at `http://127.0.0.1:8000/docs`.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks` | List all tasks |
| `GET` | `/tasks/{id}` | Get one task |
| `PUT` | `/tasks/{id}` | Replace a task |
| `DELETE` | `/tasks/{id}` | Delete a task |

Example create request:

```json
{
  "title": "Write README",
  "description": "Document setup and run steps",
  "status": "todo"
}
```

Valid task statuses are `todo`, `in_progress`, and `done`. Missing records return `404`; invalid bodies return `422`.
