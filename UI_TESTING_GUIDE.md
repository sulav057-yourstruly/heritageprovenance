# UI Testing Guide - Step by Step

This guide walks you through testing all the new UI features.

## Prerequisites

Make sure both servers are running:

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open: **http://localhost:5173**

---

## Test 1: Dashboard (Home Page)

**What to test:**
- Visual design and navigation

**Steps:**
1. Open http://localhost:5173
2. You should see the Dashboard with:
   - Purple gradient navigation bar
   - "Provenance" brand name
   - 5 feature cards (Actors, Ingest, Events, Anchor, Verify)
   - "How It Works" section with 4 steps

**Expected:**
- ✅ All navigation links visible
- ✅ Cards are clickable
- ✅ Modern, clean design
- ✅ Responsive layout

---

## Test 2: Create an Actor (NEW UI Feature!)

**What to test:**
- Generate keypair in UI
- Create actor with public key

**Steps:**

### 2.1 Generate Keypair
1. Click **"Actors"** in navigation (or go to `/actors`)
2. You should see "Generate Keypair" section
3. Click **"Generate Keypair"** button
4. Wait a moment

**Expected:**
- ✅ Button shows "Generating..." while loading
- ✅ Two key fields appear:
  - Public Key (visible)
  - Private Key (hidden by default with "Show" button)

### 2.2 View Private Key
1. Click **"Show"** button next to Private Key
2. Private key should appear (highlighted in yellow)

**Expected:**
- ✅ Private key is visible
- ✅ Button changes to "Hide"
- ✅ Private key is highlighted

### 2.3 Create Actor
1. Fill in the form:
   - **Actor ID**: `curator-001`
   - **Name**: `Museum of Digital Heritage`
2. Make sure a keypair is generated (from step 2.1)
3. Click **"Create Actor"** button

**Expected:**
- ✅ Success message appears
- ✅ Shows Actor ID, Name, and Created timestamp
- ✅ Form resets
- ✅ Keypair is cleared (ready for next actor)

**Note:** You can create multiple actors this way!

---

## Test 3: Ingest an Object

**What to test:**
- Upload file through UI
- Create genesis event

**Steps:**
1. Click **"Ingest"** in navigation (or go to `/ingest`)
2. You should see a clean form with:
   - File upload field
   - Actor ID field
   - Metadata fields (Creator, Date, Material, Rights)
3. **Select a file** (any file - text, image, PDF, etc.)
4. **Enter Actor ID**: `curator-001` (or the one you created)
5. Fill in metadata (optional):
   - Creator: `Test Creator`
   - Date: `2024-01-15`
   - Material: `Digital`
   - Rights: `Public Domain`
6. Click **"Ingest Object"** button

**Expected:**
- ✅ Button shows "Ingesting..." while loading
- ✅ Success message appears with:
  - Object ID (UUID)
  - CID (SHA-256 hash)
  - Genesis Event Hash
- ✅ All values are displayed in monospace font

---

## Test 4: Create a Provenance Event

**What to test:**
- Append event to provenance chain
- Use example payloads

**Steps:**
1. Click **"Events"** in navigation (or go to `/events`)
2. Fill in the form:
   - **Object ID**: Paste the Object ID from Test 3
   - **Event Type**: Select "Metadata Edit" from dropdown
   - **Actor ID**: `curator-001`
3. Click **"Load Example"** button next to Payload
4. The payload field should populate with example JSON
5. Click **"Create Event"** button

**Expected:**
- ✅ Example JSON loads automatically
- ✅ Success message shows Event Hash
- ✅ Event is appended to the provenance chain

**Try different event types:**
- Change Event Type to "Format Migration" → Click "Load Example" → Different example appears
- Change to "Custody Transfer" → Click "Load Example" → Another example appears

---

## Test 5: Anchor Events

**What to test:**
- Batch and anchor events
- View anchor results

**Steps:**
1. Click **"Anchor"** in navigation (or go to `/anchor`)
2. Read the explanation of what anchoring does
3. Click **"Anchor Events"** button

**Expected:**
- ✅ Button shows "Anchoring Events..." while loading
- ✅ Success message appears with:
  - Batch ID
  - Merkle Root (hash)
  - Event Count
  - Anchored At (timestamp)

**Note:** If no unanchored events exist, you'll get an error message (this is expected).

---

## Test 6: Verify an Object (Original File)

**What to test:**
- Verify the original file
- View timeline visualization

**Steps:**
1. Click **"Verify"** in navigation (or go to `/verify`)
2. **Drag and drop** the same file you ingested in Test 3
   - OR click the drop zone to select file
3. You should see:
   - File name and size displayed
   - File icon
4. Click **"Verify Object"** button

**Expected:**
- ✅ Button shows "Verifying..." while loading
- ✅ Verification report appears with:
  - ✅ **CID Match:** Pass (green)
  - ✅ **Chain Valid:** Pass (green)
  - ✅ **Signatures Valid:** Pass (green)
  - ✅ **Anchored:** Yes (if you anchored in Test 5)
- ✅ Timeline shows all events:
  - INGESTION event (first)
  - METADATA_EDIT event (second, if you created it)
  - Green checkmarks for valid signatures
  - Timestamps and actor IDs
  - Anchored status badges

---

## Test 7: Verify a Modified File (Tamper Detection)

**What to test:**
- System detects file tampering

**Steps:**
1. Take the file you ingested
2. **Modify it** (change one byte, add text, etc.)
3. Go to **"Verify"** page
4. Drag and drop the **modified file**
5. Click **"Verify Object"**

**Expected:**
- ❌ **CID Match:** Fail (red)
- ❌ **Chain Valid:** Fail (red)
- ❌ **Signatures Valid:** Fail (red)
- Error message: "CID mismatch: file CID ... not found in database"

**This proves tamper detection works!**

---

## Test 8: Full Workflow Test

**Complete end-to-end workflow:**

1. **Create Actor** (`/actors`)
   - Generate keypair
   - Create actor: `museum-a`

2. **Ingest Object** (`/ingest`)
   - Upload a file
   - Use actor: `museum-a`
   - Save the Object ID

3. **Create Event** (`/events`)
   - Use the Object ID
   - Event Type: "Metadata Edit"
   - Actor: `museum-a`
   - Use example payload

4. **Anchor Events** (`/anchor`)
   - Click "Anchor Events"
   - Save the Merkle Root

5. **Verify Object** (`/verify`)
   - Upload original file
   - Should show all checks passing
   - Timeline shows 2 events (Ingestion + Metadata Edit)
   - Both events should show as anchored

---

## Visual Design Checklist

As you test, verify:

- ✅ **Navigation bar** has purple gradient
- ✅ **Active page** is highlighted in nav
- ✅ **Cards** have white background with shadows
- ✅ **Buttons** have gradient and hover effects
- ✅ **Forms** have focus states (blue border when clicking)
- ✅ **Success messages** are green with checkmarks
- ✅ **Error messages** are red
- ✅ **File upload** shows file name and size
- ✅ **Timeline** has visual indicators (green/red dots)
- ✅ **Code blocks** use monospace font
- ✅ **Icons** appear in cards and buttons

---

## Troubleshooting

### "Actor not found" error
- Make sure you created an actor first (Test 2)
- Check the Actor ID spelling (case-sensitive)

### "Object not found" error
- Make sure you ingested an object first (Test 3)
- Check the Object ID is correct

### "No unanchored events" error
- This is normal if you already anchored all events
- Create a new event first, then anchor

### Frontend won't load
- Check backend is running on port 8000
- Check browser console for errors
- Verify `npm run dev` is running

### API errors
- Check backend terminal for error messages
- Verify database exists: `backend/data/provenance.db`
- Check API docs: http://localhost:8000/docs

---

## Success Criteria

Your UI is working correctly if:

1. ✅ All pages load without errors
2. ✅ Navigation works between all pages
3. ✅ You can create actors through UI
4. ✅ You can ingest objects through UI
5. ✅ You can create events through UI
6. ✅ You can anchor events through UI
7. ✅ You can verify objects through UI
8. ✅ Timeline visualization shows events correctly
9. ✅ Tamper detection works (modified files fail)
10. ✅ All visual elements look modern and polished

---

## Quick Test (5 minutes)

If you're short on time, test these critical features:

1. **Dashboard** → Should load and show all cards
2. **Actors** → Generate keypair → Create actor
3. **Ingest** → Upload file → Get Object ID
4. **Verify** → Upload same file → Should pass all checks

This verifies the core workflow works!

