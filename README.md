# Games Vault

## Tech Stack

### Front-end

- Next.js
- TypeScript
- CSS

### Back-end

- Pyhton
- FastApi

## Folders

- backend – Contains the main server logic
- chatbot – Temporary folder containing tested chatbot logic
- frontend – User interface and visual components of the application
- db – PostgreSQL Docker image, database backup and restore script

## Installation

Prerequisites:

- Node.js (v18+)
- Python (3.10+)

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

## Docker

project has setup docker system for whole project: backend, frontend, postgresSQL server.

1. Create the `.env` file (sets the database password):

```
cp .env.example .env
```

2. Run:

```
docker compose up --build --watch
```

| Service         | Host port |
| --------------- | --------- |
| web (frontend)  | 3000      |
| api (backend)   | 8000      |
| db (PostgreSQL) | 5433      |

The database is restored from `db/GamesVault_DB.backup` on first start. Docker uses Python 3.12 and Node 20.
