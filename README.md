# Games Vault

Games Vault is a web app for browsing, organizing and discovering Steam games. You can search and filter the full Steam catalog by genre, tag, platform and language, build your own game library (or import it from your Steam account), and chat with an AI assistant. The assistant recommends games and answers questions about them using semantic search over the game database.

## Tech Stack

### Front-end

- Next.js
- TypeScript
- CSS

### Back-end

- Pyhton
- FastApi
- LangGraph + Gemini

### Database

- PostgreSQL
- pgvector extension

## Folders

- backend – Contains the main server logic
- frontend – User interface and visual components of the application
- db – PostgreSQL Docker image, database backup and restore script

## Installation (Docker)

project has setup docker system for whole project: backend, frontend, postgresSQL server.

Requires Docker Compose 2.22+ (for `--watch`).

1. Create the `.env` file and fill in the values from `.env.example`:

```
cp .env.example .env
```

2. Run with build (first time, or after changing a Dockerfile or anything in `db/`):

```
docker compose up --build --watch
```

3. Run (normal use):

```
docker compose up --watch
```

| Service         | Host port |
| --------------- | --------- |
| web (frontend)  | 3000      |
| api (backend)   | 8000      |
| db (PostgreSQL) | 5433      |

The database is restored from `db/GamesVault_DB.backup` only on first start (empty volume). To restore a changed backup, run `docker compose down -v` first (this deletes the database data). Docker uses Python 3.12 and Node 20.

## Installation (without Docker)

Prerequisites:

- Node.js (v18+)
- Python (3.10+)
- PostgreSQL (v16+)
- pgvector extension

### Database Setup (PostgreSQL & pgvector)

The database is provided as a backup file:

`db/GamesVault_DB.backup`

To run the project locally, install PostgreSQL and the `pgvector` extension, create the database, and restore it from this backup.

1. Install PostgreSQL

Install PostgreSQL on your system. Make sure the PostgreSQL command-line tools (`psql` and `pg_restore`) are available.

Verify the installation:

```bash
psql --version
pg_restore --version
```

If the commands are not recognized, add the PostgreSQL bin directory to your system PATH or use the full path to the executables.

2. Install pgvector

`pgvector` is a PostgreSQL extension required by the project for vector storage and similarity search.

Official repository and installation instructions: https://github.com/pgvector/pgvector

3. Create the Database

Connect to PostgreSQL using the configured port. The example below uses port 5432:

```bash
psql -U postgres -p 5432 -d postgres
```

Create the database:

```sql
CREATE DATABASE GamesVault;
```

4. Restore the Database from Backup

Run this command from the project root directory:

```bash
pg_restore -U postgres -p 5432 -d gamesvault -v db/GamesVault_DB.backup
```

Enter the PostgreSQL password when prompted.

**Note:** The `pgvector` extension must be installed on the PostgreSQL server. If the restore reports that the `vector` extension is missing, enable it in the target database:

```bash
psql -U postgres -p 5432 -d gamesvault -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Then retry the restore if necessary. If the backup contains existing database objects, resolve any conflicts reported by `pg_restore` before retrying.

5. Verify the Database

List the restored tables:

```bash
psql -U postgres -p 5432 -d gamesvault -c "\dt"
```

Check whether `pgvector` is enabled:

```bash
psql -U postgres -p 5432 -d gamesvault -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
```

The database should now contain the tables and data provided by `GamesVault_DB.backup`.

### Front-end Setup

1. Navigate to the folder:

```
cd frontend
```

2. Install dependencies:

```
npm install
```

3. (Optional) Set the API address. Defaults to `http://localhost:8000`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:

```
npm run dev
```

5. Open website:

```
http://localhost:3000/
```

### Back-end Setup

1. Navigate to the folder:

```
cd backend
```

2. Create and activate a virtual environment:

```
python -m venv .venv
```

- On Windows:

```
.venv\Scripts\activate
```

- On macOS/Linux:

```
source .venv/bin/activate
```

3. Install required libraries:

```
pip install -r requirements.txt
```

4. Add .env file with link to postgreSQL server

```env
DB_LINK=
```

5. Run the Univorn server:

```
uvicorn main:app --port 8000
```

## In progress:

-
