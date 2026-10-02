export default function About() {
  return (
    <section className="section-sm">
      <div className="container" style={{ maxWidth: 800 }}>
        <div className="page-header">
          <h1>About</h1>
          <p className="lead">
            AI Resume Analyzer is a full-stack portfolio project for AI/ML, Python, GenAI, and software
            development roles.
          </p>
        </div>

        <div className="card stack-gap">
          <div>
            <h2>Tagline</h2>
            <p>Analyze your resume. Discover your strengths. Improve your career.</p>
          </div>

          <div>
            <h2>What this project demonstrates</h2>
            <ul>
              <li>Python + FastAPI REST APIs</li>
              <li>React + Vite frontend with a SaaS-style dashboard</li>
              <li>PDF/DOCX file processing</li>
              <li>Rule-based NLP-style skill &amp; section detection</li>
              <li>Modular AI service ready for LLM integration</li>
              <li>SQLite persistence for analysis reports</li>
              <li>Error handling, validation, and secure file handling basics</li>
            </ul>
          </div>

          <div>
            <h2>Important note</h2>
            <p className="muted">
              Scores are <strong>estimated</strong> for learning and portfolio use. They do not represent a
              real ATS vendor score and are not a guarantee of interviews or job offers.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
