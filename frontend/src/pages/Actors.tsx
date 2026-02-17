import { useState } from 'react'
import { apiClient } from '../lib/api'
import './Actors.css'

function Actors() {
  const [actorId, setActorId] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [keypair, setKeypair] = useState<{ private_key: string; public_key: string } | null>(null)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [showPrivateKey, setShowPrivateKey] = useState(false)

  const handleGenerateKeypair = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.generateKeypair()
      setKeypair(response)
      setResult(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate keypair')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateActor = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!actorId || !name) {
      setError('Actor ID and Name are required')
      return
    }

    setLoading(true)
    setError(null)
    try {
      // If keypair was generated, use it; otherwise let backend derive it
      const response = await apiClient.createActor({
        actor_id: actorId,
        name: name,
        pubkey_ed25519: keypair?.public_key || '',
      })
      setResult(response)
      // Reset form
      setActorId('')
      setName('')
      setKeypair(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create actor')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="actors-page">
      <div className="page-header">
        <h1>Manage Actors</h1>
        <p className="subtitle">Create and manage institutions/curators for provenance tracking</p>
      </div>

      <div className="card">
        <h2>Generate Keypair</h2>
        <p className="card-description">
          Generate a new Ed25519 keypair for signing provenance events. The private key should be stored securely.
        </p>
        <button 
          onClick={handleGenerateKeypair} 
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? 'Generating...' : 'Generate Keypair'}
        </button>

        {keypair && (
          <div className="keypair-result">
            <div className="key-display">
              <label>Public Key (will be stored with actor):</label>
              <div className="key-value">{keypair.public_key}</div>
            </div>
            <div className="key-display">
              <label>
                Private Key (store securely - you'll need this for signing events):
                <button
                  type="button"
                  onClick={() => setShowPrivateKey(!showPrivateKey)}
                  className="toggle-key-btn"
                >
                  {showPrivateKey ? 'Hide' : 'Show'}
                </button>
              </label>
              {showPrivateKey && (
                <div className="key-value private-key">{keypair.private_key}</div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h2>Create Actor</h2>
        <p className="card-description">
          Register a new actor (institution or curator) with the generated public key.
        </p>
        <form onSubmit={handleCreateActor} className="actor-form">
          <div className="form-group">
            <label htmlFor="actorId">Actor ID *</label>
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
            <label htmlFor="name">Name *</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Museum of Digital Heritage"
              required
            />
          </div>

          {!keypair && (
            <div className="info-box">
              <strong>Note:</strong> You can generate a keypair to see how it works, or skip it - the system will automatically derive a keypair for this actor ID.
            </div>
          )}

          <button 
            type="submit" 
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Creating...' : 'Create Actor'}
          </button>
        </form>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <div className="alert alert-success">
          <h3>✓ Actor Created Successfully</h3>
          <p><strong>Actor ID:</strong> {result.actor_id}</p>
          <p><strong>Name:</strong> {result.name}</p>
          <p><strong>Created:</strong> {new Date(result.created_at).toLocaleString()}</p>
        </div>
      )}
    </div>
  )
}

export default Actors

