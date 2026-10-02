import { Link } from 'react-router-dom'
import { FileText, Gauge, Lightbulb, Upload } from 'lucide-react'

const steps = [
  {
    icon: Upload,
    title: '1. Upload your resume',
    text: 'Provide a text-based PDF or DOCX file. The app validates format and size before processing.',
  },
  {
    icon: FileText,
    title: '2. Extract & analyze',
    text: 'The backend extracts text, detects sections, and matches skills from a modular catalog.',
  },
  {
    icon: Gauge,
    title: '3. Estimate scores',
    text: 'An Estimated ATS Compatibility Score and optional Job Match percentage are calculated transparently.',
  },
  {
    icon: Lightbulb,
    title: '4. Review recommendations',
    text: 'Get actionable suggestions for summary, experience, projects, and missing skills on a dashboard.',
  },
]

export default function HowItWorks() {
  return (
    <section className="section-sm">
      <div className="container">
        <div className="page-header">
          <h1>How It Works</h1>
          <p className="lead">
            A clear pipeline from upload to insights — designed so you can explain every layer in an interview.
          </p>
        </div>

        <div className="grid-2">
          {steps.map(({ icon: Icon, title, text }) => (
            <article key={title} className="card">
              <div className="feature-icon">
                <Icon size={22} aria-hidden="true" />
              </div>
              <h3>{title}</h3>
              <p className="muted">{text}</p>
            </article>
          ))}
        </div>

        <div className="card" style={{ marginTop: '1.5rem' }}>
          <h2>AI Architecture</h2>
          <p className="muted">
            Analysis goes through a modular <span className="mono">ai_service</span>. Today it uses a
            rule-based fallback so the app works without an API key. Later you can set{' '}
            <span className="mono">AI_PROVIDER=openai</span> and implement the LLM hooks without rewriting
            the UI or API routes.
          </p>
          <Link to="/analyze" className="btn btn-primary" style={{ marginTop: '0.75rem' }}>
            Try it now
          </Link>
        </div>
      </div>
    </section>
  )
}
