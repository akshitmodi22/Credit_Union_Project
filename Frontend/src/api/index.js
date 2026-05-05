const BASE = '/api'

async function request(url, options = {}) {
  const res = await fetch(`${BASE}${url}`, options)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export const getHealth        = () => request('/health')
export const getModelHealth   = () => request('/model-health')
export const getMergeStatus   = () => request('/merge-status')
export const mergePredictions = () => request('/merge-predictions', { method: 'POST' })

export const smartQuery = ({ model, tier, branch, county, age_band, income_band, life_stage, min_prob, top_n }) => {
  const qp = new URLSearchParams()
  qp.set('model', model)
  if (top_n)       qp.set('top_n', top_n)
  if (tier)        qp.set('tier', tier)
  if (branch)      qp.set('branch', branch)
  if (county)      qp.set('county', county)
  if (age_band)    qp.set('age_band', age_band)
  if (income_band) qp.set('income_band', income_band)
  if (life_stage)  qp.set('life_stage', life_stage)
  if (min_prob)    qp.set('min_prob', min_prob)
  return request(`/smart-query?${qp}`, { method: 'POST' })
}

export const getAvailableFilters = (model) => request(`/available-filters?model=${model}`)
export const runPredictions      = (model) => request(`/run-predictions?model=${model}`, { method: 'POST' })
export const runRetrain          = (model) => request(`/retrain?model=${model}`, { method: 'POST' })

export const getUnifiedReport = (branch) => {
  const qp = new URLSearchParams()
  if (branch) qp.set('branch', branch)
  return request(`/unified-report?${qp}`, { method: 'POST' })
}

export const generateChart = ({ model, group_by = 'branch_assignment', tier }) => {
  const qp = new URLSearchParams({ model, group_by })
  if (tier) qp.set('tier', tier)
  return request(`/generate-chart?${qp}`, { method: 'POST' })
}
