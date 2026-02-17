import { useEffect, useState } from 'react'
import {
  apiClient,
  ContributionRequestDetail,
  SubmissionSummary,
} from '../lib/api'
import { useAuth } from '../contexts/AuthContext'
import './Ingest.css'

type Tab = 'requests' | 'submissions'

function AdminDashboard() {
  const { user } = useAuth()
  const [tab, setTab] = useState<Tab>('requests')
  const [requests, setRequests] = useState<ContributionRequestDetail[]>([])
  const [submissions, setSubmissions] = useState<SubmissionSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [reqs, subs] = await Promise.all([
        apiClient.getContributionRequests('pending'),
        apiClient.getSubmissions('pending'),
      ])
      setRequests(reqs)
      setSubmissions(subs)
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Failed to load admin data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const handleApproveRequest = async (id: string) => {
    setLoading(true)
    setError(null)
    try {
      await apiClient.approveRequest(id)
      await load()
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Failed to approve request')
    } finally {
      setLoading(false)
    }
  }

  const handleRejectRequest = async (id: string) => {
    const reason = window.prompt('Reason for rejection?')
    if (!reason) return
    setLoading(true)
    setError(null)
    try {
      await apiClient.rejectRequest(id, reason)
      await load()
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Failed to reject request')
    } finally {
      setLoading(false)
    }
  }

  const handleApproveSubmission = async (id: string) => {
    setLoading(true)
    setError(null)
    try {
      await apiClient.approveSubmission(id)
      await load()
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Failed to approve submission')
    } finally {
      setLoading(false)
    }
  }

  const handleRejectSubmission = async (id: string) => {
    const feedback = window.prompt('Feedback for contributor?')
    if (!feedback) return
    setLoading(true)
    setError(null)
    try {
      await apiClient.rejectSubmission(id, feedback)
      await load()
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Failed to reject submission')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="ingest-page">
      <div className="page-header">
        <div>
          <h1>Admin Dashboard</h1>
          <p className="subtitle">
            Review contributor requests and submissions for the Kathmandu Cultural Heritage Archive.
          </p>
        </div>
        <div className="subtitle">
          Signed in as <strong>{user?.name}</strong> ({user?.email}) · role: {user?.role}
        </div>
      </div>

      <div className="card">
        <div className="tab-header" style={{ marginBottom: '1rem' }}>
          <button
            className={`btn btn-secondary ${tab === 'requests' ? 'active' : ''}`}
            onClick={() => setTab('requests')}
          >
            Contribution Requests
          </button>
          <button
            className={`btn btn-secondary ${tab === 'submissions' ? 'active' : ''}`}
            onClick={() => setTab('submissions')}
            style={{ marginLeft: '0.5rem' }}
          >
            Pending Submissions
          </button>
        </div>

        {loading && <div className="subtitle">Loading…</div>}
        {error && <div className="alert alert-error">{error}</div>}

        {tab === 'requests' && !loading && (
          <div>
            <h2>Pending Contribution Requests</h2>
            {requests.length === 0 && (
              <p className="subtitle">No pending contribution requests.</p>
            )}
            <table className="timeline-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Sample Title</th>
                  <th>Submitted</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {requests.map((r) => (
                  <tr key={r.request_id}>
                    <td>{r.name}</td>
                    <td>{r.email}</td>
                    <td>{r.sample_item_title}</td>
                    <td>{new Date(r.submitted_at).toLocaleString()}</td>
                    <td>
                      <button
                        className="btn btn-primary"
                        type="button"
                        onClick={() => handleApproveRequest(r.request_id)}
                      >
                        Approve
                      </button>
                      <button
                        className="btn btn-secondary"
                        type="button"
                        onClick={() => handleRejectRequest(r.request_id)}
                        style={{ marginLeft: '0.5rem' }}
                      >
                        Reject
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'submissions' && !loading && (
          <div>
            <h2>Pending Submissions</h2>
            {submissions.length === 0 && (
              <p className="subtitle">No pending submissions.</p>
            )}
            <table className="timeline-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Contributor</th>
                  <th>Status</th>
                  <th>Submitted</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {submissions.map((s) => (
                  <tr key={s.submission_id}>
                    <td>{s.object_title || s.object_id}</td>
                    <td>{s.submitted_at ? new Date(s.submitted_at).toLocaleString() : '—'}</td>
                    <td>{s.status}</td>
                    <td>{new Date(s.submitted_at).toLocaleString()}</td>
                    <td>
                      <button
                        className="btn btn-primary"
                        type="button"
                        onClick={() => handleApproveSubmission(s.submission_id)}
                      >
                        Approve
                      </button>
                      <button
                        className="btn btn-secondary"
                        type="button"
                        onClick={() => handleRejectSubmission(s.submission_id)}
                        style={{ marginLeft: '0.5rem' }}
                      >
                        Reject
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default AdminDashboard

