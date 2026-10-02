import { useEffect, useState } from 'react'

const STEPS = [
  'Extracting resume text',
  'Analyzing skills',
  'Checking ATS compatibility',
  'Comparing job requirements',
  'Generating recommendations',
]

/**
 * Professional multi-step loading animation during analysis.
 */
export default function LoadingSteps({ active = true }) {
  const [step, setStep] = useState(0)

  useEffect(() => {
    if (!active) return undefined
    setStep(0)
    const id = setInterval(() => {
      setStep((s) => (s < STEPS.length - 1 ? s + 1 : s))
    }, 900)
    return () => clearInterval(id)
  }, [active])

  return (
    <div className="card loading-panel" aria-live="polite" aria-busy="true">
      <div className="spinner" aria-hidden="true" />
      <h2>Analyzing your resume...</h2>
      <p className="muted">AI-assisted analysis is running with the rule-based engine (works without an API key).</p>
      <ol className="steps-list">
        {STEPS.map((label, index) => {
          let status = ''
          if (index < step) status = 'done'
          else if (index === step) status = 'active'
          return (
            <li key={label} className={status}>
              <span className="step-dot" aria-hidden="true" />
              <span>
                Step {index + 1}: {label}
                {status === 'done' ? ' ✓' : ''}
              </span>
            </li>
          )
        })}
      </ol>
    </div>
  )
}
