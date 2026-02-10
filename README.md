# Digital Heritage Provenance System

A functional prototype that cryptographically proves the provenance, authenticity, and custodial history of digital cultural heritage objects (scans, 3D models, audio) across institutional boundaries.

## Architecture

- **Backend**: FastAPI (Python) with SQLite database
- **Frontend**: React + TypeScript (Vite)
- **Cryptography**: SHA-256 for hashing, Ed25519 for digital signatures
- **Anchoring**: Mock anchoring (JSON file) - can be extended to blockchain

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to use the application.

### Creating an Actor

Before ingesting objects, create an actor (institution/curator):

```bash
cd backend
python scripts/create_actor.py curator-001 "Museum of Digital Heritage"
```

This generates a keypair. Use the actor_id (e.g., `curator-001`) when ingesting objects.

## Features

- **Object Ingestion**: Upload files with metadata, generate CID, create genesis event
- **Event Logging**: Append signed events to provenance chain (metadata edits, migrations, custody transfers)
- **Merkle Anchoring**: Batch events and anchor Merkle roots (mock implementation)
- **Verification**: Drag-and-drop file verification with integrity checks and timeline visualization
- **JSON-LD Export**: Export provenance data for cross-archive compatibility

## API Documentation

When the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Success Metrics

- **Tamper Evidence**: System detects file modifications via CID mismatch
- **Non-Repudiation**: Signed events cannot be denied (signature verification)
- **Persistence**: Provenance records survive local database deletion (via anchored Merkle roots)

