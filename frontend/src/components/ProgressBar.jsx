/**
 * Horizontal progress bar with accessible label.
 */
export default function ProgressBar({ label, value = 0 }) {
  const safe = Math.max(0, Math.min(100, Number(value) || 0))
  return (
    <div className="progress-row">
      <span className="progress-label">{label}</span>
      <div
        className="progress-track"
        role="progressbar"
        aria-valuenow={safe}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label}
      >
        <div className="progress-fill" style={{ width: `${safe}%` }} />
      </div>
      <span className="progress-value">{safe}%</span>
    </div>
  )
}
