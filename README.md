# Games Vault

## Tech Stack

### Front-end

- Next.js
- TypeScript
- CSS
- Build Tool: Vite

### Back-end

- Pyhton
- FastApi

## Folders

- backend – Contains the main server logic
- chatbot – Temporary folder containing tested chatbot logic
- frontend – User interface and visual components of the application

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

3. Start the development server:

```
npm run dev
```

4. Open website:

```
http://localhost:80/
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
source venv/bin/activate
```

3. Install required libraries:

```
pip install -r requirements.txt
```

4. Run the Univorn server:

```
uvicorn main:app --port 4000
```
