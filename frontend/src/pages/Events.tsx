import { useState } from 'react'
import { apiClient } from '../lib/api'
import './Events.css'

function Events() {
  const [objectId, setObjectId] = useState('')
  const [eventType, setEventType] = useState('METADATA_EDIT')
  const [actorId, setActorId] = useState('')
  const [payload, setPayload] = useState('{}')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ event_hash: string } | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!objectId || !actorId) {
      setError('Object ID and Actor ID are required')
      return
    }

    let payloadObj
    try {
      payloadObj = JSON.parse(payload)
    } catch (err) {
      setError('Invalid JSON in payload')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.createEvent(objectId, {
        event_type: eventType,
        payload: payloadObj,
        actor_id: actorId,
      })
      setResult(response)
      // Reset payload
      setPayload('{}')
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create event')
    } finally {
      setLoading(false)
    }
  }

  const examplePayloads: Record<string, string> = {
    METADATA_EDIT: JSON.stringify({
      field: 'description',
      old_value: 'Original description',
      new_value: 'Updated description'
    }, null, 2),
    MIGRATION: JSON.stringify({
      from_format: 'TIFF',
      to_format: 'JPEG',
      reason: 'Storage optimization'
    }, null, 2),
    CUSTODY_TRANSFER: JSON.stringify({
      from_actor: 'museum-a',
      to_actor: 'museum-b',
      transfer_date: '2024-01-15',
      reason: 'Loan agreement'
    }, null, 2),
    INGESTION: JSON.stringify({
      cid: 'example-cid-hash-here',
      filename: 'example-file.jpg',
      metadata: {
        creator: 'Example Creator',
        date: '2024-01-15',
        material: 'Digital',
        rights: 'Public Domain'
      }
    }, null, 2),
  }

  const handleExampleLoad = () => {
    setPayload(examplePayloads[eventType] || '{}')
  }

  return (
    <div className="events-page">
      <div className="page-header">
        <h1>Create Provenance Event</h1>
        <p className="subtitle">Append a new event to an object's provenance chain</p>
      </div>

      <div className="info-card">
        <h3>📋 What is a Provenance Event?</h3>
        <p>
          A provenance event records a change or action in an object's history. Each event is cryptographically signed
          and linked to the previous event, creating an immutable chain of custody.
        </p>
        <div className="event-types-info">
          <div className="event-type-item">
            <strong>Metadata Edit:</strong> Record changes to object metadata (description, tags, etc.)
          </div>
          <div className="event-type-item">
            <strong>Format Migration:</strong> Document when a file is converted to a different format
          </div>
          <div className="event-type-item">
            <strong>Custody Transfer:</strong> Track when an object moves between institutions or curators
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Create New Event</h2>
        <p className="card-description">
          To create an event, you need:
        </p>
        <ul className="requirements-list">
          <li>An <strong>Object ID</strong> from a previously ingested object (get this from the Ingest page)</li>
          <li>An <strong>Actor ID</strong> that exists in the system (create one on the Actors page)</li>
          <li>A <strong>Payload</strong> describing what happened (use "Load Example" for templates)</li>
        </ul>

        <form onSubmit={handleSubmit} className="event-form">
          <div className="form-group">
            <label htmlFor="objectId">
              Object ID *
              <span className="help-text">(Get this from the Ingest page after uploading a file)</span>
            </label>
            <input
              type="text"
              id="objectId"
              value={objectId}
              onChange={(e) => setObjectId(e.target.value)}
              placeholder="Paste the Object ID from your ingested object"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="eventType">Event Type *</label>
            <select
              id="eventType"
              value={eventType}
              onChange={(e) => {
                setEventType(e.target.value)
                setPayload('{}')
              }}
              required
            >
              <option value="METADATA_EDIT">Metadata Edit</option>
              <option value="MIGRATION">Format Migration</option>
              <option value="CUSTODY_TRANSFER">Custody Transfer</option>
              <option value="INGESTION">Ingestion (usually auto-created)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="actorId">
              Actor ID *
              <span className="help-text">(Create one on the Actors page if you haven't)</span>
            </label>
            <input
              type="text"
              id="actorId"
              value={actorId}
              onChange={(e) => setActorId(e.target.value)}
              placeholder="e.g., curator-001"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="payload">
              Payload (JSON) *
              <button
                type="button"
                onClick={handleExampleLoad}
                className="example-btn"
                title="Load an example payload for the selected event type"
              >
                Load Example
              </button>
            </label>
            <p className="field-help">
              The payload describes what happened. Click "Load Example" to see a template for the selected event type.
            </p>
            <textarea
              id="payload"
              value={payload}
              onChange={(e) => setPayload(e.target.value)}
              rows={10}
              placeholder='{"key": "value"}'
              required
            />
          </div>

          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? 'Creating Event...' : 'Create Event'}
          </button>
        </form>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <div className="alert alert-success">
          <h3>✓ Event Created Successfully</h3>
          <p><strong>Event Hash:</strong> <code>{result.event_hash}</code></p>
          <p className="info-text">This event has been appended to the provenance chain.</p>
        </div>
      )}
    </div>
  )
}

export default Events

