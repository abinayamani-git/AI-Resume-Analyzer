import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Download, RefreshCw } from 'lucide-react'
import ProgressBar from '../components/ProgressBar'
import ScoreRing from '../components/ScoreRing'
import SkillBadges from '../components/SkillBadges'
import StatCard from '../components/StatCard'
import { useAnalysis } from '../context/AnalysisContext'
import api from '../services/api'

export default function Results() {
  const { analysis } = useAnalysis()
  const [reportError, setReportError] = useState('')
  const [downloading, setDownloading] = useState(false)

  if (!analysis) {
    return (
      <section className="section-sm">
        <div className="container" style={{ maxWidth: 640 }}>
          <div className="card">
            <h1>Your Resume Analysis</h1>
            <p className="muted">
              No analysis is available yet. Upload a resume to generate resume insights.
            </p>
            <Link to="/analyze" className="btn btn-primary" style={{ marginTop: '1rem' }}>
              Analyze Resume
            </Link>
          </div>
        </div>
      </section>
    )
  }

  const jobMatch = analysis.job_match || {}
  const sectionScores = analysis.section_scores || {}
  const summary = analysis.summary_analysis || {}
  const personal = analysis.personal_info || {}

  const handleDownload = async () => {
    setReportError('')
    setDownloading(true)
    try {
      await api.downloadReport(analysis.analysis_id)
    } catch (err) {
      setReportError(err.message || 'Could not download the report.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <section className="section-sm">
      <div className="container stack-gap">
        <div className="dashboard-top">
          <div>
            <h1>Your Resume Analysis</h1>
            <p className="muted" style={{ margin: 0 }}>
              File: <span className="mono">{analysis.filename}</span>
              {' · '}
              Mode: <span className="mono">{analysis.analysis_mode === 'llm' ? 'LLM' : 'Rule-based fallback'}</span>
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleDownload}
              disabled={downloading}
            >
              <Download size={16} aria-hidden="true" />
              {downloading ? 'Preparing...' : 'Download Report'}
            </button>
            <Link to="/analyze" className="btn btn-secondary">
              <RefreshCw size={16} aria-hidden="true" /> New Analysis
            </Link>
          </div>
        </div>

        {reportError ? (
          <div className="alert alert-error" role="alert">
            {reportError}
          </div>
        ) : null}

        {/* Top score cards */}
        <div className="grid-4">
          <div className="card stat-card">
            <ScoreRing score={analysis.ats_score} label="Estimated ATS Compatibility Score" />
            <div className="stat-label">Estimated ATS Compatibility</div>
            <p className="disclaimer">Not a real ATS vendor score</p>
          </div>
          <StatCard
            label="Estimated Job Match"
            value={jobMatch.job_match_percentage != null ? `${jobMatch.job_match_percentage}%` : 'N/A'}
            hint={jobMatch.job_match_percentage == null ? 'Add a job description for match insights' : 'Advisory signal only'}
          />
          <StatCard
            label="Skills Found"
            value={analysis.detected_skills?.length || 0}
            hint="From modular skill catalog"
          />
          <StatCard
            label="Recommendations"
            value={analysis.recommendations?.length || 0}
            hint="AI-assisted improvement ideas"
          />
        </div>

        {/* Resume overview */}
        <div className="card">
          <h2>Resume Overview</h2>
          <div className="grid-2" style={{ marginTop: '1rem' }}>
            <div>
              <p><strong>Name:</strong> {personal.name || 'Not detected'}</p>
              <p><strong>Email:</strong> {personal.email || 'Not detected'}</p>
              <p><strong>Phone:</strong> {personal.phone || 'Not detected'}</p>
            </div>
            <div>
              <p><strong>LinkedIn:</strong> {personal.linkedin || 'Not detected'}</p>
              <p><strong>GitHub:</strong> {personal.github || 'Not detected'}</p>
              <p><strong>Sections:</strong> {(analysis.detected_sections || []).join(', ') || 'Limited structure detected'}</p>
            </div>
          </div>
        </div>

        {/* Skill analysis */}
        <div className="card">
          <h2>Skill Analysis</h2>
          <div className="grid-3" style={{ marginTop: '1rem' }}>
            <div>
              <h3>Detected Skills</h3>
              <SkillBadges skills={analysis.detected_skills} />
            </div>
            <div>
              <h3>Strong Skills</h3>
              <SkillBadges skills={analysis.strong_skills} variant="strong" />
            </div>
            <div>
              <h3>Missing / Recommended</h3>
              <SkillBadges skills={analysis.missing_skills || analysis.recommended_skills} variant="missing" />
            </div>
          </div>
        </div>

        {/* Section scores */}
        <div className="card">
          <h2>Section Scores</h2>
          <div style={{ marginTop: '1rem' }}>
            <ProgressBar label="Resume Structure" value={sectionScores.resume_structure} />
            <ProgressBar label="Skills" value={sectionScores.skills} />
            <ProgressBar label="Experience" value={sectionScores.experience} />
            <ProgressBar label="Projects" value={sectionScores.projects} />
            <ProgressBar label="Keywords" value={sectionScores.keywords} />
            <ProgressBar label="Readability" value={sectionScores.readability} />
          </div>
          {analysis.ats_breakdown ? (
            <p className="disclaimer">
              ATS breakdown — Keywords: {analysis.ats_breakdown.keyword_relevance}/25 · Skills:{' '}
              {analysis.ats_breakdown.skills}/20 · Experience: {analysis.ats_breakdown.experience}/20 ·
              Projects: {analysis.ats_breakdown.projects}/15 · Education: {analysis.ats_breakdown.education}/10 ·
              Structure: {analysis.ats_breakdown.resume_structure}/10
            </p>
          ) : null}
        </div>

        {/* Job match */}
        <div className="card">
          <h2>Job Match Analysis</h2>
          {jobMatch.job_match_percentage == null ? (
            <p className="muted">{jobMatch.explanation || 'No job description was provided for this analysis.'}</p>
          ) : (
            <>
              <p className="lead" style={{ marginTop: '0.5rem' }}>
                Estimated Job Match: <strong>{jobMatch.job_match_percentage}%</strong>
              </p>
              <p className="muted">{jobMatch.explanation}</p>
              <div className="grid-2" style={{ marginTop: '1rem' }}>
                <div>
                  <h3>Matched Skills</h3>
                  <SkillBadges skills={jobMatch.matched_skills} variant="matched" />
                </div>
                <div>
                  <h3>Missing Skills</h3>
                  <SkillBadges skills={jobMatch.missing_skills} variant="missing" />
                </div>
              </div>
              <div className="detail-block">
                <h3>Important Keywords</h3>
                <SkillBadges skills={jobMatch.important_keywords} />
              </div>
              <div className="detail-block">
                <h3>Experience Alignment</h3>
                <p className="muted">{jobMatch.experience_alignment}</p>
                <h3>Project Alignment</h3>
                <p className="muted">{jobMatch.project_alignment}</p>
              </div>
            </>
          )}
        </div>

        {/* Recommendations */}
        <div className="card">
          <h2>AI-Powered Resume Recommendations</h2>
          <p className="muted">AI-assisted suggestions based on your actual resume analysis.</p>
          <ul>
            {(analysis.recommendations || []).map((rec) => (
              <li key={rec}>{rec}</li>
            ))}
          </ul>
        </div>

        {/* Summary analysis */}
        <div className="card">
          <h2>Resume Summary Analysis</h2>
          <div className="detail-block">
            <h3>Current Summary</h3>
            <p>{summary.current_summary || 'No summary detected.'}</p>
          </div>
          <div className="detail-block">
            <h3>Issues Detected</h3>
            <ul>
              {(summary.issues_detected || []).map((issue) => (
                <li key={issue}>{issue}</li>
              ))}
            </ul>
          </div>
          <div className="detail-block">
            <h3>Improved Summary</h3>
            <p>{summary.improved_summary}</p>
          </div>
        </div>

        {/* Projects */}
        <div className="card">
          <h2>Projects</h2>
          {(analysis.projects || []).length === 0 ? (
            <p className="muted">No projects detected. Consider adding a Projects section.</p>
          ) : (
            analysis.projects.map((project) => (
              <article key={project.name} className="item-card">
                <h3>{project.name}</h3>
                <SkillBadges skills={project.technologies} />
                <p className="muted">{project.description || 'No description extracted.'}</p>
                <p><strong>Detected strengths:</strong> {(project.strengths || []).join(' ')}</p>
                <p><strong>Suggested improvements:</strong> {(project.improvements || []).join(' ')}</p>
              </article>
            ))
          )}
        </div>

        {/* Experience */}
        <div className="card">
          <h2>Experience</h2>
          {(analysis.experience || []).length === 0 ? (
            <p className="muted">No experience entries detected.</p>
          ) : (
            analysis.experience.map((exp, idx) => (
              <article key={`${exp.company}-${exp.role}-${idx}`} className="item-card">
                <h3>{exp.role || 'Role not detected'}{exp.company ? ` · ${exp.company}` : ''}</h3>
                <p className="muted">{exp.duration || 'Duration not detected'}</p>
                <SkillBadges skills={exp.skills} />
                <ul>
                  {(exp.responsibilities || []).slice(0, 6).map((r) => (
                    <li key={r}>{r}</li>
                  ))}
                </ul>
                <p className="disclaimer">
                  Signals — Action verbs: {exp.has_action_verbs ? 'Yes' : 'No'} · Technical skills:{' '}
                  {exp.has_technical_skills ? 'Yes' : 'No'} · Quantifiable results:{' '}
                  {exp.has_quantifiable_results ? 'Yes' : 'No'}
                </p>
                <p><strong>Suggested improvements:</strong> {(exp.improvements || []).join(' ')}</p>
              </article>
            ))
          )}
        </div>

        {/* Education */}
        <div className="card">
          <h2>Education</h2>
          {(analysis.education || []).length === 0 ? (
            <p className="muted">No education entries detected.</p>
          ) : (
            analysis.education.map((ed, idx) => (
              <article key={`${ed.degree}-${idx}`} className="item-card">
                <h3>{ed.degree || ed.details}</h3>
                <p className="muted">
                  {ed.institution || 'Institution not clearly detected'}
                  {ed.year ? ` · ${ed.year}` : ''}
                </p>
              </article>
            ))
          )}
        </div>

        {(analysis.certifications || []).length > 0 || (analysis.achievements || []).length > 0 ? (
          <div className="grid-2">
            <div className="card">
              <h2>Certifications</h2>
              <ul>
                {(analysis.certifications || []).map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </div>
            <div className="card">
              <h2>Achievements</h2>
              <ul>
                {(analysis.achievements || []).map((a) => (
                  <li key={a}>{a}</li>
                ))}
              </ul>
            </div>
          </div>
        ) : null}
      </div>
    </section>
  )
}
