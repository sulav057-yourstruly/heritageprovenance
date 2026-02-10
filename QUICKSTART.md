# Quick Start Guide

## Prerequisites

- Python 3.10 or higher
- Node.js 16+ and npm (for frontend)

## Step 1: Setup Backend

Open a terminal in the project root and run:

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional, but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -e .

# Create data directories (if they don't exist)
# On Windows PowerShell:
New-Item -ItemType Directory -Force -Path data\binaries
# On macOS/Linux:
mkdir -p data/binaries

# Run the backend server
uvicorn app.main:app --reload --port 8000
```

**Note**: The `pyproject.toml` is configured to exclude virtual environments (`venv`, `myenv`, `env`) and data directories from package discovery, so the installation should work even if these directories exist.

The backend API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

**Keep this terminal open!**

## Step 2: Setup Frontend

Open a **new terminal** in the project root and run:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at: http://localhost:5173

**Keep this terminal open too!**

## Step 3: Create an Actor (First Time Setup)

Before ingesting objects, you need to create an actor (institution/curator).

Open a **third terminal** (or use the backend terminal if you stopped it):

```bash
cd backend

# Activate virtual environment if not already active
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Create an actor
python scripts/create_actor.py curator-001 "Museum of Digital Heritage"
```

This will output:
- Actor ID: `curator-001`
- Public Key: (base64 encoded)
- **Private Key**: (save this securely - you'll need it for signing events)

**Note**: For the MVP, the system will auto-generate keys if you don't provide a private key, but it's better to create actors explicitly.

## Step 4: Use the Application

1. **Open your browser** and go to: http://localhost:5173

2. **Ingest an Object**:
   - Click on "Ingest" (or go to http://localhost:5173)
   - Select a file (any file - image, document, etc.)
   - Enter Actor ID: `curator-001` (or the one you created)
   - Fill in metadata (optional): Creator, Date, Material, Rights
   - Click "Ingest"
   - You'll receive: Object ID, CID, and Genesis Event Hash

3. **Add Events** (Optional):
   - Use the API at http://localhost:8000/docs
   - POST `/objects/{object_id}/events`
   - Event types: `METADATA_EDIT`, `MIGRATION`, `CUSTODY_TRANSFER`

4. **Anchor Events**:
   - Use the API: POST `/anchor`
   - This batches unanchored events and creates a Merkle root
   - The root is stored in `backend/data/anchors.json`

5. **Verify an Object**:
   - Go to "Verify" page (http://localhost:5173/verify)
   - Drag and drop the same file you ingested
   - Click "Verify"
   - View the verification report and provenance timeline

## Troubleshooting

### Backend Issues

- **Port 8000 already in use**: Change the port in the uvicorn command: `--port 8001`
- **Module not found**: Make sure you activated the virtual environment and installed dependencies
- **Database errors**: Delete `backend/data/provenance.db` and restart (this resets the database)

### Frontend Issues

- **Port 5173 already in use**: Vite will automatically use the next available port
- **Cannot connect to API**: Make sure the backend is running on port 8000
- **npm install fails**: Try deleting `node_modules` and `package-lock.json`, then run `npm install` again

### Common Issues

- **Actor not found**: Create an actor first using the script
- **CORS errors**: The backend CORS is configured for localhost:5173. If using a different port, update `backend/app/main.py`

## Testing the Success Metrics

### 1. Tamper Evidence
- Ingest a file
- Verify it (should pass)
- Modify the file (change 1 byte)
- Verify again (should fail with CID mismatch)

### 2. Non-Repudiation
- Ingest a file with an actor
- Verify signatures are valid
- Try to modify an event in the database (manually)
- Verify again (signature should fail)

### 3. Persistence
- Ingest objects and anchor events
- Delete `backend/data/provenance.db`
- Keep `backend/data/anchors.json`
- Re-import events from JSON-LD export
- Verify against anchored Merkle roots

## Next Steps

- Explore the API documentation at http://localhost:8000/docs
- Try ingesting different file types
- Create multiple actors and transfer custody
- Export JSON-LD and examine the provenance graph

