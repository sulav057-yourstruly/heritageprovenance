# Testing Guide - Provenance System

This guide walks you through testing all features of the provenance system.

## Prerequisites

- Backend dependencies installed (`pip install -e .` in backend/)
- Frontend dependencies installed (`npm install` in frontend/)
- Two terminal windows ready

---

## Step 1: Start the Backend

**Terminal 1:**

```bash
cd backend
# Activate venv if you created one
venv\Scripts\activate  # Windows
# OR: source venv/bin/activate  # Mac/Linux

# Start the server
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify:** Open http://localhost:8000/health in your browser. You should see:
```json
{"status":"ok"}
```

---

## Step 2: Start the Frontend

**Terminal 2:**

```bash
cd frontend
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Verify:** Open http://localhost:5173 in your browser. You should see the navigation with "Ingest" and "Verify" links.

---

## Step 3: Create an Actor

**Terminal 3 (or use Terminal 1 in a new tab):**

```bash
cd backend
venv\Scripts\activate  # If using venv
python scripts/create_actor.py curator-001 "Museum of Digital Heritage"
```

**Expected output:**
```
Actor created successfully!
Actor ID: curator-001
Name: Museum of Digital Heritage
Public Key: <base64-encoded-public-key>
Private Key (store securely): <base64-encoded-private-key>
```

**Save the Private Key** - you'll need it for signing events (though the MVP auto-generates if missing).

**Verify via API:** Open http://localhost:8000/docs and try:
- GET `/actors` (if we add this endpoint) or check the database

---

## Step 4: Ingest an Object

**Using the Web UI:**

1. Go to http://localhost:5173 (or click "Ingest" in the nav)
2. Click "Choose File" and select any file (e.g., a text file, image, PDF)
3. Enter Actor ID: `curator-001`
4. Fill in metadata (optional):
   - Creator: `Test Creator`
   - Date: `2024-01-15`
   - Material: `Digital`
   - Rights: `Public Domain`
5. Click "Ingest"

**Expected result:**
- Success message showing:
  - Object ID: `<uuid>`
  - CID: `<sha256-hash>`
  - Genesis Event Hash: `<hash>`

**Verify via API:**
- Open http://localhost:8000/docs
- Try `POST /ingest` with the same parameters
- Check that `backend/data/binaries/` contains the uploaded file

---

## Step 5: Add a Provenance Event

**Using the API (http://localhost:8000/docs):**

1. Find `POST /objects/{object_id}/events`
2. Use the Object ID from Step 4
3. Request body:
```json
{
  "event_type": "METADATA_EDIT",
  "payload": {
    "field": "description",
    "old_value": "Original",
    "new_value": "Updated description"
  },
  "actor_id": "curator-001"
}
```
4. Add query parameter: `private_key` (optional - system will auto-generate if missing)
5. Click "Execute"

**Expected result:**
```json
{
  "event_hash": "<new-event-hash>"
}
```

**Verify:**
- Check that a new event was created in the database
- The event should link to the previous event via `prev_event_hash`

---

## Step 6: Anchor Events

**Using the API (http://localhost:8000/docs):**

1. Find `POST /anchor`
2. Click "Execute"

**Expected result:**
```json
{
  "batch_id": "<uuid>",
  "merkle_root": "<merkle-root-hash>",
  "anchored_at": "2024-01-15T...",
  "event_count": 2
}
```

**Verify:**
- Check `backend/data/anchors.json` - it should contain the anchor record
- The file should have a JSON array with at least one anchor object

---

## Step 7: Verify an Object (Success Case)

**Using the Web UI:**

1. Go to http://localhost:5173/verify (or click "Verify" in nav)
2. Drag and drop the **same file** you ingested in Step 4
3. Click "Verify"

**Expected result:**
- ✅ **CID Match:** Pass
- ✅ **Chain Valid:** Pass
- ✅ **Signatures Valid:** Pass
- ✅ **Anchored:** Yes (if you anchored in Step 6)
- **Timeline:** Shows all events with green checkmarks

**Verify the Timeline:**
- Should show "INGESTION" event first
- Should show "METADATA_EDIT" event second (if you added it)
- Each event should show:
  - Valid signature indicator (green dot)
  - Timestamp
  - Actor ID
  - Anchored status (if applicable)

---

## Step 8: Test Tamper Detection (Failure Case)

**This tests the "Tamper Evidence" success metric:**

1. Take the file you ingested
2. **Modify it** (change one byte, add text, etc.)
   - For a text file: add a space or change a character
   - For an image: edit it slightly
3. Go to http://localhost:5173/verify
4. Drag and drop the **modified file**
5. Click "Verify"

**Expected result:**
- ❌ **CID Match:** Fail
- ❌ **Chain Valid:** Fail (or N/A)
- **Errors:** Should show "CID mismatch: file CID ... not found in database"

**This proves:** The system detects file tampering via CID mismatch.

---

## Step 9: Test Non-Repudiation

**This tests that signatures cannot be forged:**

**Option A: Via Database (Advanced)**
1. Use a SQLite browser or command line to open `backend/data/provenance.db`
2. Find an event in the `events` table
3. Modify the `payload_json` field (change any value)
4. Save and close
5. Verify the same file again

**Expected result:**
- ✅ CID Match: Pass (file unchanged)
- ✅ Chain Valid: Pass
- ❌ **Signatures Valid:** Fail
- **Errors:** Should show "Invalid signature for event ..."

**This proves:** Even if someone modifies stored events, signature verification fails.

**Option B: Via API (Easier)**
- The signature verification happens automatically during verification
- If you modify an event's payload in the database, the next verification will catch it

---

## Step 10: Test Persistence (Anchoring)

**This tests that provenance survives database deletion:**

1. Note the Object ID and CID from Step 4
2. Check `backend/data/anchors.json` - it should have anchor records
3. **Delete the database:** `del backend\data\provenance.db` (Windows) or `rm backend/data/provenance.db` (Mac/Linux)
4. **Keep** `backend/data/anchors.json`
5. Restart the backend server
6. The database will be recreated (empty)
7. The anchors file still exists with Merkle roots

**Expected result:**
- Database is empty (no objects/events)
- `anchors.json` still contains the Merkle roots
- You can verify that the anchored state exists (though you'd need to re-import events to fully verify)

**This proves:** Anchored Merkle roots persist even if the local database is deleted.

**To fully test persistence:**
- Export JSON-LD before deleting: `GET /objects/{object_id}/export.jsonld`
- Delete database
- Re-import from JSON-LD (would need a re-import script)
- Verify against anchored Merkle roots

---

## Step 11: Test JSON-LD Export

**Using the API (http://localhost:8000/docs):**

1. Find `GET /objects/{object_id}/export.jsonld`
2. Use the Object ID from Step 4
3. Click "Execute"

**Expected result:**
- JSON-LD document with:
  - `@context` with PROV, Dublin Core, PREMIS namespaces
  - Object information
  - All provenance events as `prov:wasGeneratedBy` activities
  - Event relationships via `prov:wasInformedBy`

**Verify:**
- The JSON-LD should be valid and parseable
- Events should be linked in chronological order
- Each event should reference its actor

---

## Quick Test Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads and shows navigation
- [ ] Actor creation works
- [ ] Object ingestion works (file upload + CID generation)
- [ ] Event creation works (appends to chain)
- [ ] Anchoring works (Merkle root stored)
- [ ] Verification works (original file passes)
- [ ] Tamper detection works (modified file fails)
- [ ] Timeline visualization shows events correctly
- [ ] JSON-LD export works

---

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify all dependencies are installed: `pip list`
- Check for Python version: `python --version` (needs 3.10+)

### Frontend won't start
- Check if port 5173 is in use (Vite will auto-use next port)
- Verify Node.js: `node --version`
- Try deleting `node_modules` and reinstalling: `rm -rf node_modules && npm install`

### Actor not found error
- Make sure you created an actor first
- Check actor ID spelling (case-sensitive)

### Verification fails unexpectedly
- Make sure you're using the exact same file that was ingested
- Check browser console for errors
- Verify backend logs for errors

### Database errors
- Delete `backend/data/provenance.db` to reset
- Make sure `backend/data/` directory exists and is writable

---

## Success Criteria

Your system is working correctly if:

1. ✅ **Tamper Evidence:** Modified files fail verification
2. ✅ **Non-Repudiation:** Invalid signatures are detected
3. ✅ **Persistence:** Anchored Merkle roots survive database deletion
4. ✅ **Chain Integrity:** Events are properly linked via `prev_event_hash`
5. ✅ **Visualization:** Timeline shows all events with correct status indicators

