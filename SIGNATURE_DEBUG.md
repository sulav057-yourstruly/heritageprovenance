# Signature Verification Debug Guide

## The Problem

Signatures are showing as invalid even though:
- ✅ CID matches
- ✅ Chain is valid
- ✅ Events are anchored

## Root Cause

The issue is likely one of these:

1. **Timestamp Mismatch**: The timestamp used for signing doesn't exactly match the timestamp reconstructed during verification
2. **Key Mismatch**: The actor's public key doesn't match the derived key used for signing
3. **Payload Mismatch**: The payload JSON doesn't match exactly (whitespace, key order, etc.)

## What I Fixed

1. **Unified Timestamp**: Now using the SAME timestamp for both signing and storing
   - Before: `datetime.utcnow()` for signing, `datetime.now(timezone.utc)` for storing (different times!)
   - After: Get one timestamp, use it for both

2. **Deterministic Keys**: Always derive keys from `actor_id`
   - Same `actor_id` = same keypair
   - Actor's public key is auto-updated during ingest

3. **Better Verification**: Uses derived public key (matches signing key)

## Testing Steps

### Step 1: Delete Old Database

**CRITICAL:** Old events were signed with mismatched timestamps. Delete the database:

```bash
# Windows
del backend\data\provenance.db

# Mac/Linux
rm backend/data/provenance.db
```

### Step 2: Restart Backend

The backend should auto-reload, but if not:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Step 3: Fresh Test

1. **Create Actor:**
   - Go to Actors page
   - Actor ID: `test-actor-001`
   - Name: `Test`
   - Create (no need to generate keypair)

2. **Ingest Object:**
   - Go to Ingest page
   - Upload a file
   - Actor ID: `test-actor-001`
   - Ingest

3. **Verify:**
   - Go to Verify page
   - Upload the same file
   - Check results

**Expected:** All 4 status boxes should be green, including "Signatures Valid: ✓ Pass"

## If Still Failing

### Check Backend Logs

Look for error messages in the backend terminal. The verification code now logs:
- Signature verification errors
- Event data being verified
- Canonical bytes

### Manual Debug

You can test signature verification directly:

1. Get the event hash from the verification page
2. Check the backend logs for the exact error
3. Compare the signed timestamp vs. reconstructed timestamp

### Common Issues

1. **Old Data**: If you didn't delete the database, old events will still fail
2. **Actor Mismatch**: Make sure you're using the same actor_id for ingest and verify
3. **File Mismatch**: Make sure you're verifying the exact same file you ingested

## Expected Behavior After Fix

- ✅ Same timestamp used for signing and storing
- ✅ Deterministic key derivation (same actor_id = same key)
- ✅ Exact timestamp reconstruction during verification
- ✅ All signatures should validate correctly
