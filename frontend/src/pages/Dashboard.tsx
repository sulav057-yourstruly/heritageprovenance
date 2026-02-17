import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient, ItemSummary } from '../lib/api'
import './Dashboard.css'

function Dashboard() {
  const [items, setItems] = useState<ItemSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [heritageType, setHeritageType] = useState('')
  const [culture, setCulture] = useState('')
  const [location, setLocation] = useState('')
  const navigate = useNavigate()

  const loadItems = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.getGallery({
        q: query || undefined,
        heritage_type: heritageType || undefined,
        culture: culture || undefined,
        location: location || undefined,
      })
      setItems(data)
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Failed to load gallery')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadItems()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <h1>Kathmandu Cultural Heritage Archive</h1>
          <p className="subtitle">
            Public gallery of curated Kathmandu Valley heritage items. Browse first; identity only when
            earned.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/request-contribution')}>
          Request to Contribute
        </button>
      </div>

      <div className="gallery-layout">
        <aside className="filter-sidebar">
          <h3>Filter</h3>
          <label>
            Search
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Title, location, keyword…"
            />
          </label>
          <label>
            Heritage type
            <select value={heritageType} onChange={(e) => setHeritageType(e.target.value)}>
              <option value="">Any</option>
              <option value="artwork">Artwork</option>
              <option value="photograph">Photograph</option>
              <option value="manuscript">Manuscript</option>
              <option value="architecture">Architecture</option>
              <option value="artifact">Artifact</option>
            </select>
          </label>
          <label>
            Culture
            <input
              type="text"
              value={culture}
              onChange={(e) => setCulture(e.target.value)}
              placeholder="e.g. Newar, Tibetan Buddhist"
            />
          </label>
          <label>
            Location
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Patan Museum"
            />
          </label>
          <button className="btn btn-secondary" onClick={loadItems}>
            Apply
          </button>
        </aside>

        <section className="gallery-grid-section">
          {loading && <div className="muted-text">Loading archive…</div>}
          {error && <div className="alert alert-error">{error}</div>}

          {!loading && !error && items.length === 0 && (
            <div className="muted-text">No items match these filters yet.</div>
          )}

          <div className="gallery-grid">
            {items.map((item) => (
              <button
                key={item.object_id}
                className="archive-card"
                onClick={() => navigate(`/items/${item.object_id}`)}
              >
                <div className="archive-card-image">
                  {item.primary_photo_path ? (
                    <img
                      src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/${item.primary_photo_path}`}
                      alt={item.title}
                    />
                  ) : (
                    <div className="archive-card-placeholder">No image</div>
                  )}
                </div>
                <div className="archive-card-body">
                  <h3>{item.title}</h3>
                  <p className="archive-card-meta">
                    {item.heritage_type || 'Heritage item'}
                    {item.location ? ` · ${item.location}` : ''}
                  </p>
                  {item.culture && <p className="archive-card-tag">{item.culture}</p>}
                </div>
              </button>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

export default Dashboard

