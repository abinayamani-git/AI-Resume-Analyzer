import { useCallback, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle2, FileUp, Upload } from 'lucide-react'
import LoadingSteps from '../components/LoadingSteps'
import { useAnalysis } from '../context/AnalysisContext'
import api from '../services/api'
import {
  ALLOWED_EXTENSIONS,
  MAX_FILE_SIZE_MB,
  formatBytes,
  validateResumeFile,
} from '../utils/fileValidation'

export default function Analyze() {
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const { setAnalysis, setUploadMeta } = useAnalysis()

  const [file, setFile] = useState(null)
  const [uploadInfo, setUploadInfo] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState('')
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)

  const acceptFile = useCallback((nextFile) => {
    setError('')
    const validationError = validateResumeFile(nextFile)
    if (validationError) {
      setFile(null)
      setUploadInfo(null)
      setError(validationError)
      return
    }
    setFile(nextFile)
    setUploadInfo(null)
  }, [])

  const onDrop = (event) => {
    event.preventDefault()
    setDragging(false)
    const dropped = event.dataTransfer.files?.[0]
    if (dropped) acceptFile(dropped)
  }

  const handleUploadAndAnalyze = async () => {
    setError('')
    if (!file) {
      setError('Please upload a resume before analyzing.')
      return
    }

    try {
      setUploading(true)
      const uploaded = await api.uploadResume(file)
      setUploadInfo(uploaded)
      setUploadMeta(uploaded)
      setUploading(false)

      setAnalyzing(true)
      // Small delay so the loading steps are visible
      await new Promise((r) => setTimeout(r, 700))

      const result = await api.analyzeResume({
        file_id: uploaded.file_id,
        job_description: jobDescription.trim() || undefined,
      })

      setAnalysis(result)
      setAnalyzing(false)
      navigate('/results')
    } catch (err) {
      setUploading(false)
      setAnalyzing(false)
      setError(err.message || 'Analysis failed. Please try again.')
    }
  }

  if (analyzing) {
    return (
      <section className="section-sm">
        <div className="container" style={{ maxWidth: 720 }}>
          <LoadingSteps active />
        </div>
      </section>
    )
  }

  return (
    <section className="section-sm">
      <div className="container stack-gap" style={{ maxWidth: 820 }}>
        <div className="page-header">
          <h1>Upload Your Resume</h1>
          <p className="lead">Upload your resume in PDF or DOCX format.</p>
        </div>

        {error ? (
          <div className="alert alert-error" role="alert">
            {error}
          </div>
        ) : null}

        <div className="card">
          <div
            className={`upload-zone ${dragging ? 'dragging' : ''}`}
            onDragOver={(e) => {
              e.preventDefault()
              setDragging(true)
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                inputRef.current?.click()
              }
            }}
            role="button"
            tabIndex={0}
            aria-label="Upload resume via drag and drop or browse files"
          >
            <div className="upload-icon" aria-hidden="true">
              <Upload size={26} />
            </div>
            <h3>Drag and drop your resume here</h3>
            <p className="muted">or click to browse files</p>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ marginTop: '1rem' }}
              onClick={(e) => {
                e.stopPropagation()
                inputRef.current?.click()
              }}
            >
              <FileUp size={16} aria-hidden="true" /> Browse Files
            </button>
            <p className="disclaimer">
              Supported formats: {ALLOWED_EXTENSIONS.join(', ').toUpperCase()} · Max size:{' '}
              {MAX_FILE_SIZE_MB} MB
            </p>
            <input
              ref={inputRef}
              className="file-input-hidden"
              type="file"
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={(e) => {
                const selected = e.target.files?.[0]
                if (selected) acceptFile(selected)
              }}
              aria-label="Choose resume file"
            />
          </div>

          {file ? (
            <div className="alert alert-success" style={{ marginTop: '1rem' }} role="status">
              <strong style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                <CheckCircle2 size={16} aria-hidden="true" /> Resume ready
              </strong>
              <div style={{ marginTop: '0.35rem' }}>
                <span className="mono">{file.name}</span>
                <span className="muted"> · {formatBytes(file.size)}</span>
              </div>
              {uploadInfo ? <div className="muted">Resume uploaded successfully</div> : null}
            </div>
          ) : null}
        </div>

        <div className="card">
          <h2>Add Job Description</h2>
          <p className="muted">
            Optional — paste a job description to estimate how well your resume matches the role.
            Leave empty for general resume analysis.
          </p>
          <label htmlFor="job-description" className="muted" style={{ display: 'block', marginBottom: '0.5rem' }}>
            Job description
          </label>
          <textarea
            id="job-description"
            className="textarea"
            placeholder="Paste the job description here to compare your resume with the role..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
          <button
            type="button"
            className="btn btn-primary btn-lg"
            onClick={handleUploadAndAnalyze}
            disabled={!file || uploading}
          >
            {uploading ? 'Uploading...' : jobDescription.trim() ? 'Analyze Match' : 'Analyze Resume'}
          </button>
        </div>
      </div>
    </section>
  )
}
