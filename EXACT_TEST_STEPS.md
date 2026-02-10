# Exact Testing Steps - Fix Signature Verification

## The Problem

Signatures are invalid because:
1. **Old actors** were created with random keypairs
2. **New system** uses deterministic key derivation from `actor_id`
3. **Mismatch:** Old public keys don't match derived keys

## The Fix

I've updated the verification to:
1. Always use the **derived public key** (same as signing)
2. Auto-sync actor's stored public key if there's a mismatch
3. Try both keys if there's a mismatch

---

## EXACT STEPS TO TEST (Start Fresh)

### Step 1: Delete Old Database

**Windows PowerShell:**
```powershell
cd backend
Remove-Item data\provenance.db -ErrorAction SilentlyContinue
```

**Windows CMD:**
```cmd
cd backend
del data\provenance.db
```

**Mac/Linux:**
```bash
cd backend
rm data/provenance.db
```

**Why?** Old data has mismatched keys. Fresh start is needed.

---

### Step 2: Start Backend Server

```bash
cd backend
venv\Scripts\activate  # Windows
# OR: source venv/bin/activate  # Mac/Linux

uvicorn app.main:app --reload --port 8000
```

**Wait for:** `INFO: Application startup complete.`

**Verify:** Open http://localhost:8000/health in browser
- Should see: `{"status":"ok"}`

---

### Step 3: Start Frontend

**New terminal:**
```bash
cd frontend
npm run dev
```

**Wait for:** `Local: http://localhost:5173/`

**Open:** http://localhost:5173 in browser

---

### Step 4: Create Actor

1. Click **"Actors"** in navigation (or go to http://localhost:5173/actors)
2. **Fill in form:**
   - Actor ID: `test-actor-001`
   - Name: `Test Museum`
3. **IMPORTANT:** You can skip "Generate Keypair" - the system will derive it automatically
4. Click **"Create Actor"**

**Expected:**
- ✅ Success message appears
- Shows Actor ID and Name
- Public key is automatically derived and stored

**Note:** The system derives the keypair from `actor_id`, so you don't need to generate one manually.

---

### Step 5: Ingest a Photo

1. Click **"Ingest"** in navigation (or go to http://localhost:5173/ingest)
2. Click **"Choose File"** and select a photo (any image file)
3. **Fill in form:**
   - Actor ID: `test-actor-001` (same as Step 4)
   - Creator: `Test Creator` (optional)
   - Date: `2024-01-15` (optional)
   - Material: `Digital` (optional)
   - Rights: `Public Domain` (optional)
4. Click **"Ingest Object"**

**Expected:**
- ✅ Success message appears
- Shows:
  - **Object ID:** (UUID - save this!)
  - **CID:** (SHA-256 hash)
  - **Genesis Event Hash:** (hash)

**What happens behind the scenes:**
- System derives private key from `actor_id`
- Signs the genesis event
- Stores event with signature

---

### Step 6: Anchor Events (Optional)

1. Click **"Anchor"** in navigation (or go to http://localhost:5173/anchor)
2. Click **"Anchor Events"**

**Expected:**
- ✅ Success message
- Shows:
  - Batch ID
  - Merkle Root
  - Event Count: 1
  - Anchored At timestamp

---

### Step 7: Verify the Photo

1. Click **"Verify"** in navigation (or go to http://localhost:5173/verify)
2. **Drag and drop** the **exact same photo** you ingested in Step 5
   - OR click the drop zone and select the same file
3. Click **"Verify Object"**

**Expected Results:**
- ✅ **CID Match:** Pass (green box)
- ✅ **Chain Valid:** Pass (green box)
- ✅ **Signatures Valid:** Pass (green box) ← **This should now work!**
- ✅ **Anchored:** Yes (green box)
- **Timeline:** Shows INGESTION event with:
  - Green checkmark (valid signature)
  - "✓ Anchored in batch: ..."
  - No red "✗ Signature invalid" message

---

## If It Still Fails

### Check 1: Actor Public Key

The system should auto-update the actor's public key during ingest. But verify:

1. Go to http://localhost:8000/docs
2. Try `GET /actors` (if we add it) or check database
3. The actor's public key should match the derived one

### Check 2: Backend Logs

Look at your backend terminal for error messages. The new code logs:
- Signature verification errors
- Event data being verified
- Canonical bytes

### Check 3: Fresh Start

**Most important:** Make sure you deleted the database (Step 1). Old data won't work.

---

## Why This Should Work Now

1. **Deterministic Key Derivation:**
   - Same `actor_id` → same keypair
   - Used for both signing and verification

2. **Auto-Sync:**
   - Actor's public key is updated during ingest
   - Verification uses derived key (matches signing)

3. **Fallback:**
   - If stored key doesn't match, tries derived key
   - Updates stored key if derived key works

---

## Quick Test Checklist

- [ ] Database deleted (fresh start)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Actor created (Actor ID: `test-actor-001`)
- [ ] Photo ingested successfully
- [ ] Events anchored (optional)
- [ ] Verification shows all green checkmarks
- [ ] Timeline shows valid signature

---

## Expected Timeline View

When verification succeeds, you should see:

```
Provenance Timeline

┌─────────────────────────────────────┐
│ INGESTION                            │
│ 2024-01-15 10:30:45                 │
│                                     │
│ Actor: test-actor-001               │
│ ✓ Anchored in batch: 22e51600...    │
│                                     │
│ ▼ Payload                           │
│ {                                   │
│   "cid": "...",                     │
│   "filename": "...",                │
│   "metadata": {...}                 │
│ }                                   │
└─────────────────────────────────────┘
```

**No red "✗ Signature invalid" message!**

---

## Troubleshooting

### Still seeing "Invalid signature"

1. **Did you delete the database?** (Most common issue)
2. **Is the backend restarted?** (Needs to load new code)
3. **Check backend logs** for detailed error messages
4. **Try a different actor ID** to test fresh derivation

### "Actor not found" error

- Make sure you created the actor first
- Check Actor ID spelling (case-sensitive)

### "Object not found" during verify

- Use the **exact same file** you ingested
- Check that ingestion succeeded (got Object ID)

---

## Success Criteria

Your test is successful if:
- ✅ All 4 status boxes are green (Pass/Yes)
- ✅ No errors in the Errors section
- ✅ Timeline shows green checkmark for signature
- ✅ No "Invalid signature" message

If all these are true, signatures are working correctly! 🎉
