/**
 * Small metric card used on the dashboard overview row.
 */
export default function StatCard({ label, value, hint }) {
  return (
    <div className="card stat-card">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      {hint ? <p className="disclaimer">{hint}</p> : null}
    </div>
  )
}
