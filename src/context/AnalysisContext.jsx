import { createContext, useContext, useMemo, useState } from 'react'

const AnalysisContext = createContext(null)

export function AnalysisProvider({ children }) {
  const [analysis, setAnalysis] = useState({
    soilImage: null,
    soilResult: null,
    location: { latitude: '', longitude: '', district: '', mandal: '' },
    weather: null,
    farmer: {},
    recommendation: null,
  })

  const updateAnalysis = (updates) => setAnalysis((current) => ({ ...current, ...updates }))
  const value = useMemo(() => ({ analysis, updateAnalysis }), [analysis])

  return <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>
}

export function useAnalysis() {
  return useContext(AnalysisContext)
}
