# Provenance Backend

FastAPI backend for digital heritage provenance tracking.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Create data directory:
```bash
mkdir -p data/binaries
```

4. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Creating Actors

Before ingesting objects, you need to create an actor (institution/curator). You can:

1. Use the API endpoint `POST /actors` (see API docs)
2. Use the helper script:
```bash
python scripts/create_actor.py curator-001 "Museum of Digital Heritage"
```

The script will generate a keypair and display both public and private keys. Store the private key securely for signing events.

## Environment

The backend uses SQLite (stored in `data/provenance.db`) and mock anchoring (stored in `data/anchors.json`).

## MVP Note on Private Keys

For the MVP, private keys can be passed as form fields or query parameters. In production, this should be handled through secure key management (HSM, key vault, etc.).

