# How to Use the Events Page

## What is a Provenance Event?

A **provenance event** records something that happened to a digital heritage object. Think of it like a log entry in a chain of custody:

- **Who** did something (Actor ID)
- **What** happened (Event Type)
- **When** it happened (automatically recorded)
- **Details** about what happened (Payload)

Each event is cryptographically signed and linked to the previous event, creating an unbreakable chain.

---

## Step-by-Step Guide

### Step 1: Get an Object ID

Before creating an event, you need an object that was already ingested:

1. Go to the **"Ingest"** page
2. Upload a file
3. Fill in the form and click "Ingest Object"
4. **Copy the Object ID** from the success message (it's a UUID like `a1b2c3d4-...`)

### Step 2: Get an Actor ID

You need an actor (institution/curator) to sign the event:

1. Go to the **"Actors"** page
2. Generate a keypair (if you haven't)
3. Create an actor with an ID like `curator-001`
4. **Remember the Actor ID** you created

### Step 3: Create the Event

1. Go to the **"Events"** page
2. Fill in the form:

   **Object ID:**
   - Paste the Object ID from Step 1
   - Example: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`

   **Event Type:**
   - Select from dropdown:
     - **Metadata Edit**: For changes to metadata
     - **Format Migration**: When converting file formats
     - **Custody Transfer**: When object moves between institutions
     - **Ingestion**: Usually auto-created, rarely needed manually

   **Actor ID:**
   - Enter the Actor ID from Step 2
   - Example: `curator-001`

   **Payload:**
   - Click **"Load Example"** to see a template
   - The example changes based on the Event Type you selected
   - Edit the JSON to match your situation
   - Must be valid JSON format

3. Click **"Create Event"**

---

## Example Workflow

### Example 1: Edit Metadata

**Scenario:** You want to update the description of an object.

1. **Object ID:** `abc123...` (from Ingest page)
2. **Event Type:** `Metadata Edit`
3. **Actor ID:** `curator-001`
4. **Payload:** Click "Load Example" and you'll see:
   ```json
   {
     "field": "description",
     "old_value": "Original description",
     "new_value": "Updated description"
   }
   ```
5. Edit the values to match your change
6. Click "Create Event"

### Example 2: Format Migration

**Scenario:** You converted a TIFF file to JPEG.

1. **Object ID:** `abc123...`
2. **Event Type:** `Format Migration`
3. **Actor ID:** `curator-001`
4. **Payload:** Click "Load Example":
   ```json
   {
     "from_format": "TIFF",
     "to_format": "JPEG",
     "reason": "Storage optimization"
   }
   ```
5. Update with your actual formats and reason
6. Click "Create Event"

### Example 3: Custody Transfer

**Scenario:** Object is being loaned to another museum.

1. **Object ID:** `abc123...`
2. **Event Type:** `Custody Transfer`
3. **Actor ID:** `curator-001` (current custodian)
4. **Payload:** Click "Load Example":
   ```json
   {
     "from_actor": "museum-a",
     "to_actor": "museum-b",
     "transfer_date": "2024-01-15",
     "reason": "Loan agreement"
   }
   ```
5. Fill in the actual transfer details
6. Click "Create Event"

---

## Common Questions

### Q: What if I don't have an Object ID?
**A:** Go to the "Ingest" page first and upload a file. You'll get an Object ID in the success message.

### Q: What if I don't have an Actor ID?
**A:** Go to the "Actors" page and create one. It only takes a minute!

### Q: What should I put in the Payload?
**A:** Click "Load Example" - it will show you a template based on the Event Type you selected. Just edit the values to match your situation.

### Q: Can I create multiple events for the same object?
**A:** Yes! Each event gets appended to the chain. They'll all show up in the timeline when you verify the object.

### Q: What happens after I create an event?
**A:** The event is cryptographically signed and added to the provenance chain. You can see it when you verify the object on the "Verify" page.

---

## Tips

- ✅ Always use "Load Example" first - it shows you the expected format
- ✅ Make sure your JSON is valid (no trailing commas, proper quotes)
- ✅ Use the same Actor ID that was used to ingest the object (or create a new one)
- ✅ After creating events, go to "Anchor" page to batch and anchor them
- ✅ View the full chain on the "Verify" page

---

## What Happens Behind the Scenes

When you create an event:

1. The system links it to the previous event (creates the chain)
2. It cryptographically signs the event with the actor's private key
3. It stores the event in the database
4. The event hash is computed and returned

This ensures:
- **Non-repudiation**: The actor can't deny creating the event
- **Chain integrity**: Events are linked in order
- **Tamper evidence**: Any modification breaks the chain
