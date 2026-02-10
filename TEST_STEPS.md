# Exact Testing Steps - Signature Verification Fix

## Problem
Signatures are showing as invalid because:
1. Actors created before the fix have mismatched keypairs
2. The system now uses deterministic key derivation, but old actors don't match

## Solution: Fresh Start

**IMPORTANT:** Delete the database and start fresh to test properly.

---

## Step-by-Step Test (Fresh Database)

### Step 1: Delete Old Database
```bash
# Windows PowerShell:
Remove-Item backend\data\provenance.db -ErrorAction SilentlyContinue

# OR Windows CMD:
del backend\data\provenance.db

# Mac/Linux:
rm backend/data/provenance.db
```

### Step 2: Start Backend
```bash
cd backend
venv\Scripts\activate  # Windows
# OR: source venv/bin/activate  # Mac/Linux
uvicorn app.main:app --reload --port 8000
```

**Verify:** Check http://localhost:8000/health - should return `{"status":"ok"}`

### Step 3: Start Frontend
```bash
cd frontend
npm run dev
```

**Verify:** Open http://localhost:5173 - should see the dashboard

### Step 4: Create Actor
1. Go to **"Actors"** page (http://localhost:5173/actors)
2. **Option A (Recommended):** Just fill in:
   - Actor ID: `test-actor-001`
   - Name: `Test Museum`
   - Click "Create Actor" (no need to generate keypair - system will derive it)
3. **Option B:** Generate keypair first, then create actor (for educational purposes)

**Expected:** Success message with Actor ID and Name

### Step 5: Ingest Object
1. Go to **"Ingest"** page (http://localhost:5173/ingest)
2. Select any file (photo, document, etc.)
3. Enter Actor ID: `test-actor-001` (same as Step 4)
4. Fill metadata (optional):
   - Creator: `Test Creator`
   - Date: `2024-01-15`
   - Material: `Digital`
   - Rights: `Public Domain`
5. Click **"Ingest Object"**

**Expected:** Success message with:
- Object ID (UUID)
- CID (SHA-256 hash)
- Genesis Event Hash

**Save the Object ID** - you'll need it for Step 6

### Step 6: Anchor Events (Optional but Recommended)
1. Go to **"Anchor"** page (http://localhost:5173/anchor)
2. Click **"Anchor Events"**

**Expected:** Success message with:
- Batch ID
- Merkle Root
- Event Count: 1
- Anchored At timestamp

### Step 7: Verify Object
1. Go to **"Verify"** page (http://localhost:5173/verify)
2. Drag and drop the **exact same file** you ingested in Step 5
3. Click **"Verify Object"**

**Expected Results:**
- ✅ **CID Match:** Pass (green)
- ✅ **Chain Valid:** Pass (green)
- ✅ **Signatures Valid:** Pass (green) ← **This should now work!**
- ✅ **Anchored:** Yes (green)
- **Timeline:** Shows INGESTION event with green checkmark

---

## If Signatures Still Fail

### Debug Steps:

1. **Check Actor Public Key:**
   - The actor's public key should match the derived one
   - System automatically updates it during ingest

2. **Check Event Timestamp:**
   - The timestamp format might still be mismatched
   - We fixed this, but old events might have issues

3. **Verify Key Derivation:**
   - Same `actor_id` should always produce same keypair
   - Test by creating another object with same actor - should work

### Quick Fix for Existing Data:

If you have existing data and don't want to delete it:

1. **Update Actor's Public Key:**
   - The system should auto-update it during ingest
   - But you can manually verify by checking the database

2. **Re-create Events:**
   - Delete old events
   - Re-ingest the object
   - This will create new events with correct signatures

---

## Expected Behavior

After following these steps with a **fresh database**:

1. ✅ Actor creation works
2. ✅ Object ingestion works
3. ✅ Event signatures are valid
4. ✅ Verification passes all checks
5. ✅ Timeline shows valid signatures

---

## Troubleshooting

### "Actor not found" error
- Make sure you created the actor first
- Check the Actor ID spelling (case-sensitive)

### "Object not found" during verify
- Make sure you're using the exact same file
- Check that ingestion succeeded

### Signatures still invalid
- **Most likely:** You're using old data from before the fix
- **Solution:** Delete database and start fresh (Step 1)
- The deterministic key derivation only works for new actors/events

### Database locked error
- Stop the backend server
- Delete the database file
- Restart the server

---

## Key Points

1. **Deterministic Key Derivation:** Same `actor_id` = same keypair
2. **Automatic Key Sync:** Actor's public key is updated during ingest to match derived key
3. **Fresh Start Required:** Old data won't work - delete database and start fresh
4. **No Manual Keys Needed:** System derives keys automatically from actor_id
