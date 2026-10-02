/**
 * Centralized API client for the AI Resume Analyzer backend.
 * Keep all fetch calls here — do not scatter them across components.
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function parseError(response) {
  try {
    const data = await response.json()
    return data.detail || data.message || 'Something went wrong. Please try again.'
  } catch {
    return 'Something went wrong. Please try again.'
  }
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_URL}${path}`, options)
  } catch {
    throw new Error(
      'Backend unavailable. Make sure the FastAPI server is running on port 8000.',
    )
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
