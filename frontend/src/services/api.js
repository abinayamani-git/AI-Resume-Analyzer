/**
 * Centralized API client for the AI Resume Analyzer backend.
 * Keep all fetch calls here — do not scatter them across components.
 */

const PRODUCTION_API_URL = 'https://ai-resume-analyzer-backend-rvbv.onrender.com'
const DEV_API_URL = 'http://localhost:8000'
const PRODUCTION_FRONTEND_HOST = 'ai-resume-analyzer-1-h3mm.onrender.com'

function isLocalUrl(url) {
  try {
    const { hostname } = new URL(url)
    return hostname === 'localhost' || hostname === '127.0.0.1'
  } catch {
    return false
  }
}

function resolveApiUrl() {
  const envUrl = (import.meta.env.VITE_API_URL || '').trim().replace(/\/$/, '')

  // When the app is served from the production frontend host, never call localhost.
  if (typeof window !== 'undefined' && window.location.hostname === PRODUCTION_FRONTEND_HOST) {
    if (envUrl && !isLocalUrl(envUrl)) return envUrl
    return PRODUCTION_API_URL
  }

  // Explicit env (local .env or Render build var) wins for non-production hosts.
  if (envUrl) return envUrl

  // Production builds without VITE_API_URL still need the Render backend.
  if (import.meta.env.PROD) return PRODUCTION_API_URL

  return DEV_API_URL
}

const API_URL = resolveApiUrl()

async function parseError(response) {
  try {
    const data = await response.json()
    return data.detail || data.message || 'Something went wrong. Please try again.'
  } catch {
    return 'Something went wrong. Please try again.'
  }
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// Render free services sleep. The first browser request while they wake often
// fails before CORS headers exist, which surfaces as a network error.
const WAKE_RETRY_DELAYS_MS = [4000, 8000, 12000, 20000]

async function request(path, options = {}) {
  let response
  for (let attempt = 0; ; attempt += 1) {
    try {
      response = await fetch(`${API_URL}${path}`, options)
    } catch {
      if (attempt < WAKE_RETRY_DELAYS_MS.length) {
        await delay(WAKE_RETRY_DELAYS_MS[attempt])
        continue
      }
      const hint = isLocalUrl(API_URL)
        ? 'Make sure the FastAPI server is running on port 8000.'
        : `Could not reach the API at ${API_URL}.`
      throw new Error(`Backend unavailable. ${hint}`)
    }

    if (
      [502, 503, 504].includes(response.status) &&
      attempt < WAKE_RETRY_DELAYS_MS.length
    ) {
      await delay(WAKE_RETRY_DELAYS_MS[attempt])
      continue
    }
    break
  }

  if (!response.ok) {
    throw new Error(await parseError(response))
  }

  // PDF download returns a blob
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/pdf')) {
    return response.blob()
  }
  return response.json()
}

export const api = {
  health() {
    return request('/api/health')
  },

  /**
   * Upload a resume file (PDF or DOCX).
   * @param {File} file
   */
  uploadResume(file) {
    const form = new FormData()
    form.append('file', file)
    return request('/api/upload', {
      method: 'POST',
      body: form,
    })
  },

  /**
   * Analyze an uploaded resume, optionally with a job description.
   * @param {{ file_id: string, job_description?: string }} payload
   */
  analyzeResume(payload) {
    return request('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  },

  /**
   * Standalone job-match comparison.
   */
  jobMatch(payload) {
    return request('/api/job-match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  },

  /**
   * Download PDF report for an analysis id.
   */
  async downloadReport(analysisId) {
    const blob = await request(`/api/report/${analysisId}`)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `resume-analysis-${analysisId.slice(0, 8)}.pdf`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  },
}

export default api
