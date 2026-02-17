import { useState } from 'react'
import { apiClient, VerificationReport } from '../lib/api'
import Timeline from '../components/Timeline'
import './Verify.css'

function Verify() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState<VerificationReport | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleVerify = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.verify(file)
      setReport(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Verification failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="verify-page">
      <div className="page-header">
        <h1>Verify Digital Heritage Object</h1>
        <p className="subtitle">Verify file integrity, chain validity, and signature authenticity</p>
      </div>
      <div className="card">
      
        <div
          className={`drop-zone ${dragActive ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-input"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <label htmlFor="file-input" className="drop-label">
            {file ? (
              <>
                <span className="file-icon">📄</span>
                <span className="file-name">{file.name}</span>
                <span className="file-size">({(file.size / 1024).toFixed(2)} KB)</span>
              </>
            ) : (
              <>
                <span className="drop-icon">📎</span>
                <span>Drag and drop a file here, or click to select</span>
              </>
            )}
          </label>
        </div>

        {file && (
          <button onClick={handleVerify} disabled={loading} className="btn btn-primary verify-button">
            {loading ? 'Verifying...' : 'Verify Object'}
          </button>
        )}

        {error && <div className="alert alert-error">{error}</div>}
      </div>

      {report && (
        <div className="card verification-report">
          <h2>Verification Report</h2>
          <div className="status-grid">
            <div className={`status-item ${report.cid_match ? 'pass' : 'fail'}`}>
              <strong>CID Match:</strong> {report.cid_match ? '✓ Pass' : '✗ Fail'}
            </div>
            <div className={`status-item ${report.chain_valid ? 'pass' : 'fail'}`}>
              <strong>Chain Valid:</strong> {report.chain_valid ? '✓ Pass' : '✗ Fail'}
            </div>
            <div className={`status-item ${report.signatures_valid ? 'pass' : 'fail'}`}>
              <strong>Signatures Valid:</strong> {report.signatures_valid ? '✓ Pass' : '✗ Fail'}
            </div>
            <div className={`status-item ${report.anchored ? 'pass' : 'warn'}`}>
              <strong>Anchored:</strong> {report.anchored ? '✓ Yes' : '⚠ Not Anchored'}
            </div>
          </div>

          {report.errors.length > 0 && (
            <div className="errors">
              <h3>Errors:</h3>
              <ul>
                {report.errors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </div>
          )}

          <Timeline events={report.timeline} />
        </div>
      )}
    </div>
  )
}

export default Verify

