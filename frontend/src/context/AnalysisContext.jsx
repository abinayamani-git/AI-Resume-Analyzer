import { createContext, useContext, useMemo, useState } from 'react'

const AnalysisContext = createContext(null)

/**
 * Holds the latest analysis result so /results can render without re-fetching.
 * Cleared only when the user starts a new analysis flow.
 */
export function AnalysisProvider({ children }) {
  const [analysis, setAnalysis] = useState(null)
  const [uploadMeta, setUploadMeta] = useState(null)

  const value = useMemo(
    () => ({
      analysis,
      setAnalysis,
      uploadMeta,
      setUploadMeta,
      clearAnalysis: () => {
        setAnalysis(null)
        setUploadMeta(null)
      },
    }),
    [analysis, uploadMeta],
  )

  return (
    <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>
  )
}

export function useAnalysis() {
  const ctx = useContext(AnalysisContext)
  if (!ctx) {
    throw new Error('useAnalysis must be used within AnalysisProvider')
  }
  return ctx
}
