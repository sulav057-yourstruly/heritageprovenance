import { useState } from 'react'
import { apiClient } from '../lib/api'
import './Ingest.css'

function Ingest() {
  const [file, setFile] = useState<File | null>(null)
  const [metadata, setMetadata] = useState({
    creator: '',
    date: '',
    material: '',
    rights: '',
  })
  const [actorId, setActorId] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ object_id: string; cid: string; genesis_event_hash: string } | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file || !actorId) {
      setError('File and Actor ID are required')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.ingest(file, metadata, actorId)
      setResult(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Ingestion failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="ingest-page">
      <div className="page-header">
        <h1>Ingest Digital Heritage Object</h1>
        <p className="subtitle">Upload files and create genesis provenance events</p>
      </div>
      <div className="card">
        <form onSubmit={handleSubmit} className="ingest-form">
        <div className="form-group">
          <label htmlFor="file">File</label>
          <input
            type="file"
            id="file"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="actorId">Actor ID</label>
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
          <label htmlFor="creator">Creator</label>
          <input
            type="text"
            id="creator"
            value={metadata.creator}
            onChange={(e) => setMetadata({ ...metadata, creator: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label htmlFor="date">Date</label>
          <input
            type="text"
            id="date"
            value={metadata.date}
            onChange={(e) => setMetadata({ ...metadata, date: e.target.value })}
            placeholder="e.g., 2024-01-01"
          />
        </div>

        <div className="form-group">
          <label htmlFor="material">Material</label>
          <input
            type="text"
            id="material"
            value={metadata.material}
            onChange={(e) => setMetadata({ ...metadata, material: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label htmlFor="rights">Rights</label>
          <input
            type="text"
            id="rights"
            value={metadata.rights}
            onChange={(e) => setMetadata({ ...metadata, rights: e.target.value })}
          />
        </div>

          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? 'Ingesting...' : 'Ingest Object'}
          </button>
        </form>

        {error && <div className="alert alert-error">{error}</div>}

        {result && (
          <div className="alert alert-success">
            <h3>✓ Ingestion Successful</h3>
            <p><strong>Object ID:</strong> <code>{result.object_id}</code></p>
            <p><strong>CID:</strong> <code>{result.cid}</code></p>
            <p><strong>Genesis Event Hash:</strong> <code>{result.genesis_event_hash}</code></p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Ingest

