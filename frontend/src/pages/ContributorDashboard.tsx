import { useEffect, useState } from 'react'
import { apiClient, ItemDetail, SubmissionSummary } from '../lib/api'
import { useAuth } from '../contexts/AuthContext'
import './Ingest.css'

function ContributorDashboard() {
  const { user } = useAuth()
  const [tab, setTab] = useState<'submissions' | 'new'>('submissions')
  const [items, setItems] = useState<ItemDetail[]>([])
  const [submissions, setSubmissions] = useState<SubmissionSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [contribs, subs] = await Promise.all([
        apiClient.myContributions(),
        apiClient.mySubmissions(),
      ])
      setItems(contribs)
      setSubmissions(subs)
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleSubmitItem = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const form = new FormData(e.currentTarget)
    setLoading(true)
    setError(null)
    try {
      await apiClient.submitItem(form)
      e.currentTarget.reset()
      setTab('submissions')
      await loadData()
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Failed to submit item')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="ingest-page">
      <div className="page-header">
        <div>
          <h1>Contributor Dashboard</h1>
          <p className="subtitle">
            Approved contributors can submit new Kathmandu heritage items for review.
          </p>
        </div>
        <div className="subtitle">
          Signed in as <strong>{user?.name}</strong> ({user?.email})
        </div>
      </div>

      <div className="card">
        <div className="tab-header" style={{ marginBottom: '1rem' }}>
          <button
            className={`btn btn-secondary ${tab === 'submissions' ? 'active' : ''}`}
            onClick={() => setTab('submissions')}
          >
            My Submissions
          </button>
          <button
            className={`btn btn-secondary ${tab === 'new' ? 'active' : ''}`}
            onClick={() => setTab('new')}
            style={{ marginLeft: '0.5rem' }}
          >
            Submit New Item
          </button>
        </div>

        {loading && <div className="subtitle">Loading…</div>}
        {error && <div className="alert alert-error">{error}</div>}

        {tab === 'submissions' && !loading && (
          <div>
            <h2>My Submissions</h2>
            {submissions.length === 0 && (
              <p className="subtitle">You have not submitted any items yet.</p>
            )}
            <table className="timeline-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Submitted</th>
                  <th>Feedback</th>
                </tr>
              </thead>
              <tbody>
                {submissions.map((s) => (
                  <tr key={s.submission_id}>
                    <td>{s.object_title || s.object_id}</td>
                    <td>{s.status}</td>
                    <td>{new Date(s.submitted_at).toLocaleString()}</td>
                    <td>{s.admin_feedback || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'new' && !loading && (
          <div>
            <h2>Submit New Heritage Item</h2>
            <p className="subtitle">
              Provide as much cultural context, references, and photographic documentation as possible.
            </p>
            <form onSubmit={handleSubmitItem} className="ingest-form">
              <div className="form-group">
                <label htmlFor="title">Title *</label>
                <input id="title" name="title" required />
              </div>
              <div className="form-group">
                <label htmlFor="description">Description *</label>
                <textarea id="description" name="description" rows={4} required />
              </div>
              <div className="form-group">
                <label htmlFor="heritage_type">Heritage Type</label>
                <select id="heritage_type" name="heritage_type">
                  <option value="">Select…</option>
                  <option value="artwork">Artwork</option>
                  <option value="photograph">Photograph</option>
                  <option value="manuscript">Manuscript</option>
                  <option value="architecture">Architecture</option>
                  <option value="artifact">Artifact</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="location">Location</label>
                <input id="location" name="location" placeholder="e.g. Patan Museum, Lalitpur" />
              </div>
              <div className="form-group">
                <label htmlFor="date_created">Date / Period</label>
                <input id="date_created" name="date_created" placeholder="e.g. 17th century" />
              </div>
              <div className="form-group">
                <label htmlFor="culture">Cultural Tradition</label>
                <input id="culture" name="culture" placeholder="e.g. Newar, Tibetan Buddhist" />
              </div>
              <div className="form-group">
                <label htmlFor="significance">Historical / Cultural Significance</label>
                <textarea id="significance" name="significance" rows={3} />
              </div>
              <div className="form-group">
                <label htmlFor="keywords">Keywords (JSON array)</label>
                <input
                  id="keywords"
                  name="keywords"
                  placeholder='["buddhism","thangka","patan_museum"]'
                />
              </div>
              <div className="form-group">
                <label htmlFor="references">References / Citations (JSON array of strings)</label>
                <input
                  id="references"
                  name="references"
                  placeholder='["Book title, year","Catalogue reference"]'
                />
              </div>
              <div className="form-group">
                <label htmlFor="primary_photo">Primary Photo *</label>
                <input id="primary_photo" name="primary_photo" type="file" accept="image/*" required />
              </div>
              <div className="form-group">
                <label htmlFor="related_photos">Related Photos (up to 5)</label>
                <input
                  id="related_photos"
                  name="related_photos"
                  type="file"
                  accept="image/*"
                  multiple
                />
              </div>
              <button className="btn btn-primary" type="submit">
                Submit for Review
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  )
}

export default ContributorDashboard

