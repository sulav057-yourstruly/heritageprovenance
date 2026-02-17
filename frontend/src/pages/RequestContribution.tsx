import { useState, useRef } from 'react'
import { apiClient } from '../lib/api'
import './Ingest.css'

type Step = 1 | 2 | 3

interface FormState {
  // Step 1
  name: string
  email: string
  affiliation: string
  bio: string
  // Step 2
  sample_item_title: string
  sample_item_description: string
  sample_location: string
  sample_culture: string
  sample_significance: string
  sample_references: string
  // Step 3
  reason: string
}

function RequestContribution() {
  const [step, setStep] = useState<Step>(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successId, setSuccessId] = useState<string | null>(null)

  const [formState, setFormState] = useState<FormState>({
    name: '',
    email: '',
    affiliation: '',
    bio: '',
    sample_item_title: '',
    sample_item_description: '',
    sample_location: '',
    sample_culture: '',
    sample_significance: '',
    sample_references: '',
    reason: '',
  })

  // Refs for file inputs (files can't be stored in state easily)
  const primaryPhotoRef = useRef<HTMLInputElement>(null)
  const relatedPhotosRef = useRef<HTMLInputElement>(null)

  // Store files separately
  const [primaryPhoto, setPrimaryPhoto] = useState<File | null>(null)
  const [relatedPhotos, setRelatedPhotos] = useState<File[]>([])

  const updateField = (field: keyof FormState, value: string) => {
    setFormState((prev) => ({ ...prev, [field]: value }))
  }

  const next = () => {
    // Validate current step before proceeding
    if (step === 1) {
      if (!formState.name || !formState.email) {
        setError('Please fill in all required fields')
        return
      }
    }
    if (step === 2) {
      if (!formState.sample_item_title || !formState.sample_item_description || !primaryPhoto) {
        setError('Please fill in all required fields and select a primary photo')
        return
      }
    }
    setError(null)
    setStep((s) => Math.min(3, s + 1) as Step)
  }

  const prev = () => {
    setError(null)
    setStep((s) => Math.max(1, s - 1) as Step)
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (!formState.reason) {
      setError('Please provide a reason for wanting to contribute')
      return
    }

    if (!primaryPhoto) {
      setError('Primary photo is required')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const form = new FormData()
      // Step 1 fields
      form.append('name', formState.name)
      form.append('email', formState.email)
      if (formState.affiliation) form.append('affiliation', formState.affiliation)
      if (formState.bio) form.append('bio', formState.bio)
      // Step 2 fields
      form.append('sample_item_title', formState.sample_item_title)
      form.append('sample_item_description', formState.sample_item_description)
      if (formState.sample_location) form.append('sample_location', formState.sample_location)
      if (formState.sample_culture) form.append('sample_culture', formState.sample_culture)
      if (formState.sample_significance) form.append('sample_significance', formState.sample_significance)
      if (formState.sample_references) form.append('sample_references', formState.sample_references)
      // Step 3 fields
      form.append('reason', formState.reason)
      // Files
      form.append('primary_photo', primaryPhoto)
      relatedPhotos.forEach((file) => {
        form.append('related_photos', file)
      })

      const res = await apiClient.submitContributionRequest(form)
      setSuccessId(res.request_id)
    } catch (e: any) {
      const detail = e.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail)) {
        // FastAPI validation errors
        setError(detail.map((d: any) => d.msg || JSON.stringify(d)).join(', '))
      } else {
        setError(e.message || 'Failed to submit request')
      }
    } finally {
      setLoading(false)
    }
  }

  if (successId) {
    return (
      <div className="ingest-page">
        <div className="page-header">
          <h1>Request Submitted</h1>
          <p className="subtitle">
            Thank you. An administrator will review your sample contribution for cultural accuracy and sourcing.
          </p>
        </div>
        <div className="card">
          <p>
            <strong>Request ID:</strong> <code>{successId}</code>
          </p>
          <p className="subtitle">
            If approved, you will receive contributor credentials. There is no self‑registration.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="ingest-page">
      <div className="page-header">
        <h1>Request to Contribute</h1>
        <p className="subtitle">
          Visitors don't have accounts. Contributor access is earned through a sample, reviewable contribution.
        </p>
      </div>

      <div className="card">
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          <span className="subtitle">
            <strong>Step {step}</strong> of 3
          </span>
        </div>

        <form onSubmit={handleSubmit} className="ingest-form">
          {step === 1 && (
            <>
              <h2>Personal Information</h2>
              <div className="form-group">
                <label htmlFor="name">Full name *</label>
                <input
                  id="name"
                  name="name"
                  value={formState.name}
                  onChange={(e) => updateField('name', e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email *</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={formState.email}
                  onChange={(e) => updateField('email', e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="affiliation">Affiliation</label>
                <input
                  id="affiliation"
                  name="affiliation"
                  placeholder="e.g. Museum, University, Community group"
                  value={formState.affiliation}
                  onChange={(e) => updateField('affiliation', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label htmlFor="bio">Brief bio</label>
                <textarea
                  id="bio"
                  name="bio"
                  rows={3}
                  value={formState.bio}
                  onChange={(e) => updateField('bio', e.target.value)}
                />
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <h2>Sample Contribution</h2>
              <div className="form-group">
                <label htmlFor="sample_item_title">Title *</label>
                <input
                  id="sample_item_title"
                  name="sample_item_title"
                  value={formState.sample_item_title}
                  onChange={(e) => updateField('sample_item_title', e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="sample_item_description">Description (cultural context) *</label>
                <textarea
                  id="sample_item_description"
                  name="sample_item_description"
                  rows={4}
                  value={formState.sample_item_description}
                  onChange={(e) => updateField('sample_item_description', e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="sample_location">Location</label>
                <input
                  id="sample_location"
                  name="sample_location"
                  placeholder="Place + region"
                  value={formState.sample_location}
                  onChange={(e) => updateField('sample_location', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label htmlFor="sample_culture">Cultural tradition</label>
                <input
                  id="sample_culture"
                  name="sample_culture"
                  placeholder="e.g. Newar, Tibetan Buddhist"
                  value={formState.sample_culture}
                  onChange={(e) => updateField('sample_culture', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label htmlFor="sample_significance">Historical significance</label>
                <textarea
                  id="sample_significance"
                  name="sample_significance"
                  rows={3}
                  value={formState.sample_significance}
                  onChange={(e) => updateField('sample_significance', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label htmlFor="sample_references">References (JSON array)</label>
                <input
                  id="sample_references"
                  name="sample_references"
                  placeholder='["Catalogue entry…","Book citation…"]'
                  value={formState.sample_references}
                  onChange={(e) => updateField('sample_references', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label htmlFor="primary_photo">Primary photo *</label>
                <input
                  id="primary_photo"
                  name="primary_photo"
                  type="file"
                  accept="image/*"
                  ref={primaryPhotoRef}
                  onChange={(e) => {
                    const file = e.target.files?.[0] || null
                    setPrimaryPhoto(file)
                  }}
                  required
                />
                {primaryPhoto && (
                  <span className="subtitle" style={{ marginTop: '0.25rem', display: 'block' }}>
                    Selected: {primaryPhoto.name}
                  </span>
                )}
              </div>
              <div className="form-group">
                <label htmlFor="related_photos">Related photos (up to 5)</label>
                <input
                  id="related_photos"
                  name="related_photos"
                  type="file"
                  accept="image/*"
                  multiple
                  ref={relatedPhotosRef}
                  onChange={(e) => {
                    const files = e.target.files ? Array.from(e.target.files).slice(0, 5) : []
                    setRelatedPhotos(files)
                  }}
                />
                {relatedPhotos.length > 0 && (
                  <span className="subtitle" style={{ marginTop: '0.25rem', display: 'block' }}>
                    Selected: {relatedPhotos.map((f) => f.name).join(', ')}
                  </span>
                )}
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <h2>Motivation</h2>
              <div className="form-group">
                <label htmlFor="reason">Why do you want to contribute? *</label>
                <textarea
                  id="reason"
                  name="reason"
                  rows={4}
                  value={formState.reason}
                  onChange={(e) => updateField('reason', e.target.value)}
                  required
                />
              </div>
              <p className="subtitle">
                Submissions are reviewed for cultural sensitivity, accuracy, and sourcing before any access is granted.
              </p>

              <div
                style={{
                  marginTop: '1rem',
                  padding: '1rem',
                  background: 'rgba(255,255,255,0.05)',
                  borderRadius: '0.5rem',
                }}
              >
                <h3 style={{ marginBottom: '0.5rem' }}>Review your submission</h3>
                <p>
                  <strong>Name:</strong> {formState.name}
                </p>
                <p>
                  <strong>Email:</strong> {formState.email}
                </p>
                {formState.affiliation && (
                  <p>
                    <strong>Affiliation:</strong> {formState.affiliation}
                  </p>
                )}
                <p>
                  <strong>Sample Item:</strong> {formState.sample_item_title}
                </p>
                {primaryPhoto && (
                  <p>
                    <strong>Photo:</strong> {primaryPhoto.name}
                  </p>
                )}
              </div>
            </>
          )}

          {error && <div className="alert alert-error">{error}</div>}

          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
            {step > 1 && (
              <button type="button" className="btn btn-secondary" onClick={prev}>
                Back
              </button>
            )}
            {step < 3 ? (
              <button type="button" className="btn btn-primary" onClick={next}>
                Continue
              </button>
            ) : (
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Submitting…' : 'Submit Request'}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  )
}

export default RequestContribution
