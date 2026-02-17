/**
 * API client for Provenance backend.
 */
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface ActorCreate {
  actor_id: string
  name: string
  pubkey_ed25519: string
}

export interface IngestRequest {
  metadata: Record<string, any>
  actor_id: string
}

export interface IngestResponse {
  object_id: string
  cid: string
  genesis_event_hash: string
}

export interface EventCreate {
  event_type: string
  payload: Record<string, any>
  actor_id: string
}

export interface EventResponse {
  event_hash: string
}

export interface AnchorResponse {
  batch_id: string
  merkle_root: string
  anchored_at: string
  event_count: number
}

export interface EventTimelineItem {
  event_hash: string
  event_type: string
  timestamp: string
  actor_id: string
  payload: Record<string, any>
  prev_event_hash: string | null
  signature_valid: boolean
  anchored: boolean
  batch_id: string | null
}

export interface VerificationReport {
  cid_match: boolean
  chain_valid: boolean
  signatures_valid: boolean
  anchored: boolean
  timeline: EventTimelineItem[]
  errors: string[]
}

// Gallery / items
export interface ItemSummary {
  object_id: string
  title: string
  heritage_type?: string
  location?: string
  culture?: string
  primary_photo_path?: string
  date_created?: string
}

export interface ItemDetail extends ItemSummary {
  description?: string
  significance?: string
  keywords?: string[]
  references?: string[]
  related_photos?: string[]
  created_at: string
  published_at?: string
}

// Auth
export interface LoginResponse {
  access_token: string
  token_type: string
  user: {
    user_id: string
    email: string
    name: string
    role: 'contributor' | 'admin'
    bio?: string
    affiliation?: string
  }
}

// Contribution request
export interface ContributionRequestSummary {
  request_id: string
  email: string
  name: string
  status: string
  submitted_at: string
}

export interface ContributionRequestDetail extends ContributionRequestSummary {
  bio?: string
  affiliation?: string
  reason: string
  sample_item_title: string
  sample_item_description: string
  sample_location?: string
  sample_culture?: string
  sample_significance?: string
  sample_references?: string[]
  sample_photos: string[]
  reviewed_by?: string
  reviewed_at?: string
  admin_notes?: string
}

export interface SubmissionSummary {
  submission_id: string
  object_id: string
  object_title?: string
  submission_type: string
  status: string
  submitted_at: string
  reviewed_at?: string
  admin_feedback?: string
}

export const apiClient = {
  async generateKeypair() {
    const res = await api.post('/actors/generate')
    return res.data
  },

  async createActor(data: ActorCreate) {
    const res = await api.post('/actors', data)
    return res.data
  },

  async ingest(file: File, metadata: Record<string, any>, actorId: string) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('metadata', JSON.stringify(metadata))
    formData.append('actor_id', actorId)
    
    const res = await api.post<IngestResponse>('/ingest', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async createEvent(objectId: string, data: EventCreate, privateKey?: string) {
    const url = `/objects/${objectId}/events${privateKey ? `?private_key=${encodeURIComponent(privateKey)}` : ''}`
    const res = await api.post<EventResponse>(url, data)
    return res.data
  },

  async anchor() {
    const res = await api.post<AnchorResponse>('/anchor')
    return res.data
  },

  async verify(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    
    const res = await api.post<VerificationReport>('/verify', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async exportJSONLD(objectId: string) {
    const res = await api.get(`/objects/${objectId}/export.jsonld`, {
      responseType: 'blob',
    })
    return res.data
  },

  // Gallery / items
  async getGallery(params?: {
    q?: string
    heritage_type?: string
    culture?: string
    location?: string
  }) {
    const res = await api.get<ItemSummary[]>('/gallery', { params })
    return res.data
  },

  async getItemDetail(objectId: string) {
    const res = await api.get<ItemDetail>(`/gallery/items/${objectId}`)
    return res.data
  },

  async getItemEvents(objectId: string) {
    const res = await api.get<EventTimelineItem[]>(`/objects/${objectId}/events`)
    return res.data
  },

  // Auth
  async login(email: string, password: string) {
    const res = await api.post<LoginResponse>('/auth/login', { email, password })
    api.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`
    return res.data
  },

  async me() {
    const res = await api.get<LoginResponse['user']>('/auth/me')
    return res.data
  },

  setToken(token: string | null) {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete api.defaults.headers.common['Authorization']
    }
  },

  // Contribution request (visitor)
  async submitContributionRequest(form: FormData) {
    const res = await api.post<ContributionRequestSummary>('/contribute/request', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  // Contributor dashboard
  async myContributions() {
    const res = await api.get<ItemDetail[]>('/my/contributions')
    return res.data
  },

  async mySubmissions() {
    const res = await api.get<SubmissionSummary[]>('/my/submissions')
    return res.data
  },

  async submitItem(form: FormData) {
    const res = await api.post('/my/items', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  // Admin dashboard
  async getContributionRequests(status?: string) {
    const res = await api.get<ContributionRequestDetail[]>('/admin/requests', {
      params: status ? { status } : undefined,
    })
    return res.data
  },

  async approveRequest(id: string, admin_notes?: string) {
    const res = await api.post(`/admin/requests/${id}/approve`, { admin_notes })
    return res.data
  },

  async rejectRequest(id: string, reason: string) {
    const res = await api.post(`/admin/requests/${id}/reject`, { reason })
    return res.data
  },

  async getSubmissions(status?: string) {
    const res = await api.get<SubmissionSummary[]>('/admin/submissions', {
      params: status ? { status } : undefined,
    })
    return res.data
  },

  async approveSubmission(id: string, admin_feedback?: string) {
    const res = await api.post(`/admin/submissions/${id}/approve`, { admin_feedback })
    return res.data
  },

  async rejectSubmission(id: string, admin_feedback: string) {
    const res = await api.post(`/admin/submissions/${id}/reject`, { admin_feedback })
    return res.data
  },
}

