/**
 * Technical skill badges (JetBrains Mono via .skill-badge).
 */
export default function SkillBadges({ skills = [], variant = 'default', emptyText = 'None detected' }) {
  if (!skills.length) {
    return <p className="muted">{emptyText}</p>
  }

  const cls =
    variant === 'strong'
      ? 'skill-badge strong'
      : variant === 'missing'
        ? 'skill-badge missing'
        : variant === 'matched'
          ? 'skill-badge matched'
          : 'skill-badge'

  return (
    <div className="badge-row" role="list" aria-label="Skills">
      {skills.map((skill) => (
        <span key={skill} className={cls} role="listitem">
          {skill}
        </span>
      ))}
    </div>
  )
}
