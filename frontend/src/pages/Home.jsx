import { Link } from 'react-router-dom'
import { ArrowRight, BarChart3, Briefcase, FileSearch, Sparkles } from 'lucide-react'

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <p className="muted" style={{ fontWeight: 500, marginBottom: '0.75rem' }}>
              AI Resume Analyzer
            </p>
            <h1>Make Your Resume AI-Ready</h1>
            <p className="lead">
              Analyze your resume, measure ATS compatibility, identify skill gaps, and discover how
              well your profile matches a job description.
            </p>
            <div className="hero-actions">
              <Link to="/analyze" className="btn btn-primary btn-lg">
                Analyze My Resume <ArrowRight size={18} aria-hidden="true" />
              </Link>
              <Link to="/how-it-works" className="btn btn-secondary btn-lg">
                How It Works
              </Link>
            </div>
          </div>

          {/* Icon / CSS illustration — no stock photos */}
          <div className="hero-visual" aria-hidden="true">
            <div className="hero-doc">
              <div className="hero-line mid" />
              <div className="hero-line" />
              <div className="hero-line short" />
              <div className="hero-line mid" style={{ marginTop: '1.25rem' }} />
              <div className="hero-line" />
              <div className="hero-line short" />
              <div style={{ display: 'flex', gap: '0.4rem', marginTop: '1rem' }}>
                <span className="skill-badge matched">Python</span>
                <span className="skill-badge matched">React</span>
                <span className="skill-badge matched">FastAPI</span>
              </div>
            </div>
            <div className="hero-score-chip">
              <div className="muted" style={{ fontSize: '0.8rem' }}>Estimated ATS</div>
              <div className="score-number">87</div>
              <div className="muted" style={{ fontSize: '0.8rem' }}>Compatibility</div>
            </div>
          </div>
        </div>
      </section>

      <section className="section" id="features">
        <div className="container">
          <div className="page-header">
            <h2>Resume Insights that Help You Improve</h2>
            <p className="lead">
              Built as a full-stack portfolio project with a modular AI layer — rule-based today,
              LLM-ready tomorrow.
            </p>
          </div>
          <div className="grid-3">
            <article className="card">
              <div className="feature-icon"><FileSearch size={22} /></div>
              <h3>Resume Analysis</h3>
              <p className="muted">
                Extract structure, skills, experience, and projects from PDF or DOCX resumes.
              </p>
            </article>
            <article className="card">
              <div className="feature-icon"><BarChart3 size={22} /></div>
              <h3>Estimated ATS Score</h3>
              <p className="muted">
                Transparent scoring across keywords, skills, experience, projects, and structure.
              </p>
            </article>
            <article className="card">
              <div className="feature-icon"><Briefcase size={22} /></div>
              <h3>Job Match Insights</h3>
              <p className="muted">
                Optionally paste a job description to estimate overlap and missing skills.
              </p>
            </article>
          </div>
        </div>
      </section>

      <section className="section-sm" style={{ paddingBottom: '4rem' }}>
        <div className="container">
          <div className="card" style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Sparkles size={18} aria-hidden="true" /> Ready to improve your resume?
              </h3>
              <p className="muted" style={{ margin: 0 }}>
                Upload a resume and get actionable recommendations in minutes.
              </p>
            </div>
            <Link to="/analyze" className="btn btn-primary">
              Analyze Resume
            </Link>
          </div>
        </div>
      </section>
    </>
  )
}
