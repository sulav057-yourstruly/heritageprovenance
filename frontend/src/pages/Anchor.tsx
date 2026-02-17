import { useState } from 'react'
import { apiClient } from '../lib/api'
import './Anchor.css'

function Anchor() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAnchor = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await apiClient.anchor()
      setResult(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to anchor events')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="anchor-page">
      <div className="page-header">
        <h1>Anchor Events</h1>
        <p className="subtitle">Batch unanchored events and create a Merkle root anchor</p>
      </div>

      <div className="card">
        <div className="anchor-info">
          <h2>What is Anchoring?</h2>
          <p>
            Anchoring creates a cryptographic checkpoint by computing a Merkle root of all unanchored events
            and storing it in the anchor file. This provides tamper-evidence and persistence even if the
            local database is deleted.
          </p>
          <ul>
            <li>Collects all events that haven't been anchored yet</li>
            <li>Computes a Merkle tree root</li>
            <li>Stores the root in <code>backend/data/anchors.json</code></li>
            <li>Generates inclusion proofs for each event</li>
          </ul>
        </div>

        <button 
          onClick={handleAnchor} 
          disabled={loading}
          className="btn btn-primary btn-large"
        >
          {loading ? 'Anchoring Events...' : 'Anchor Events'}
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <div className="alert alert-success">
          <h3>✓ Events Anchored Successfully</h3>
          <div className="result-details">
            <div className="detail-item">
              <strong>Batch ID:</strong>
              <code>{result.batch_id}</code>
            </div>
            <div className="detail-item">
              <strong>Merkle Root:</strong>
              <code>{result.merkle_root}</code>
            </div>
            <div className="detail-item">
              <strong>Event Count:</strong>
              <span>{result.event_count}</span>
            </div>
            <div className="detail-item">
              <strong>Anchored At:</strong>
              <span>{new Date(result.anchored_at).toLocaleString()}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Anchor

