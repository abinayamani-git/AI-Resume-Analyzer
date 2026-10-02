/**
 * Shared helpers for file validation and display formatting.
 */

export const MAX_FILE_SIZE_MB = 5
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
export const ALLOWED_EXTENSIONS = ['.pdf', '.docx']

export function getExtension(filename = '') {
  const idx = filename.lastIndexOf('.')
  return idx === -1 ? '' : filename.slice(idx).toLowerCase()
}

/**
 * Validate a resume File before upload.
 * Returns an error string or null if valid.
 */
export function validateResumeFile(file) {
  if (!file) return 'Please choose a resume file.'
  if (file.size === 0) return 'The selected file is empty.'
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return `File is too large. Maximum size is ${MAX_FILE_SIZE_MB} MB.`
  }
  const ext = getExtension(file.name)
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    return `Unsupported file type "${ext || 'unknown'}". Please upload a PDF or DOCX file.`
  }
  return null
}

export function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

export function scoreTone(score) {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}
