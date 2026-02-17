import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Verify.css'

function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const userData = await login(email, password)
      // Redirect based on role
      if (userData.role === 'admin') {
        navigate('/admin', { replace: true })
      } else {
        navigate('/contributor', { replace: true })
      }
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="verify-page">
      <div className="page-header">
        <h1>Contributor / Admin Login</h1>
        <p className="subtitle">
          Access is granted only after review and approval. Visitors do not need an account to browse.
        </p>
      </div>
      <div className="card">
        <form onSubmit={handleSubmit} className="ingest-form" style={{ maxWidth: 420 }}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Login'}
          </button>
          {error && <div className="alert alert-error" style={{ marginTop: '1rem' }}>{error}</div>}
        </form>

        <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
          <p className="subtitle">
            Not a contributor yet?{' '}
            <Link to="/request-contribution" style={{ color: '#61dafb' }}>
              Request contributor access
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
