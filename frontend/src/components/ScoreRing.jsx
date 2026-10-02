import { scoreTone } from '../utils/fileValidation'

/**
 * Circular estimated score indicator.
 */
export default function ScoreRing({ score = 0, label = 'Score', max = 100 }) {
  const safe = Math.max(0, Math.min(max, Number(score) || 0))
  const tone = scoreTone(safe)
  const color =
    tone === 'success' ? '#16a34a' : tone === 'warning' ? '#f59e0b' : '#dc2626'

  return (
    <div
      className="score-ring"
      style={{ '--progress': (safe / max) * 100, background: `conic-gradient(${color} calc(var(--progress) * 1%), #e2e8f0 0)` }}
      role="img"
      aria-label={`${label}: ${safe} out of ${max}`}
    >
      <div className="score-ring-inner">
        <div>
          <div className="score-ring-value">{safe}</div>
          <div className="score-ring-label">/ {max}</div>
        </div>
      </div>
    </div>
  )
}
