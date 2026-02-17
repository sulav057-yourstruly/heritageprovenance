import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Actors from './pages/Actors'
import Ingest from './pages/Ingest'
import Events from './pages/Events'
import Anchor from './pages/Anchor'
import Verify from './pages/Verify'
import Login from './pages/Login'
import ContributorDashboard from './pages/ContributorDashboard'
import AdminDashboard from './pages/AdminDashboard'
import RequestContribution from './pages/RequestContribution'
import { useAuth } from './contexts/AuthContext'
import { AuthGuard } from './components/AuthGuard'
import './App.css'

function App() {
  const location = useLocation()
  const { user, logout } = useAuth()

  return (
    <div className="app">
      <nav className="nav">
        <div className="nav-brand">
          <Link to="/">🏛️ Kathmandu Archive</Link>
        </div>
        <div className="nav-links">
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>Gallery</Link>
          <Link to="/verify" className={location.pathname === '/verify' ? 'active' : ''}>Verify</Link>

          {/* Provenance tools always visible, to keep the research UI accessible */}
          <Link
            to="/ingest"
            className={location.pathname === '/ingest' ? 'active' : ''}
          >
            Ingest
          </Link>
          <Link
            to="/events"
            className={location.pathname === '/events' ? 'active' : ''}
          >
            Events
          </Link>
          <Link
            to="/anchor"
            className={location.pathname === '/anchor' ? 'active' : ''}
          >
            Anchor
          </Link>
          <Link
            to="/actors"
            className={location.pathname === '/actors' ? 'active' : ''}
          >
            Actors
          </Link>

          {/* Role-aware links */}
          {user && (user.role === 'contributor' || user.role === 'admin') && (
            <Link
              to="/contributor"
              className={location.pathname.startsWith('/contributor') ? 'active' : ''}
            >
              My Items
            </Link>
          )}

          {user && user.role === 'admin' && (
            <Link
              to="/admin"
              className={location.pathname.startsWith('/admin') ? 'active' : ''}
            >
              Admin
            </Link>
          )}

          {!user ? (
            <Link
              to="/login"
              className={location.pathname === '/login' ? 'active' : ''}
            >
              Login
            </Link>
          ) : (
            <button className="btn btn-secondary" type="button" onClick={logout}>
              Logout ({user.name.split(' ')[0]})
            </button>
          )}
        </div>
      </nav>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          {/* legacy provenance tools still available but not primary nav */}
          <Route path="/actors" element={<Actors />} />
          <Route path="/ingest" element={<Ingest />} />
          <Route path="/events" element={<Events />} />
          <Route path="/anchor" element={<Anchor />} />
          <Route path="/verify" element={<Verify />} />
          <Route path="/request-contribution" element={<RequestContribution />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/contributor"
            element={
              <AuthGuard>
                <ContributorDashboard />
              </AuthGuard>
            }
          />
          <Route
            path="/admin"
            element={
              <AuthGuard requireAdmin>
                <AdminDashboard />
              </AuthGuard>
            }
          />
        </Routes>
      </main>
    </div>
  )
}

export default App

