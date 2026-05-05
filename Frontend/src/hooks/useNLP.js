export function parseNL(text, currentModel) {
  const l = text.toLowerCase()
  const result = { intent: 'smart_query', model: currentModel, params: {} }

  // ── Detect model ────────────────────────────────────────────
  if (l.includes('attrition') || l.includes('churn')) result.model = 'attrition'
  else if (l.includes('loan') || l.includes('offer')) result.model = 'loan'
  else if (l.includes('propensity') || l.includes('deposit')) result.model = 'propensity'
  else if (l.includes('master') || l.includes('all model') || l.includes('unified')) result.model = 'master'

  // ── Detect intent ───────────────────────────────────────────
  if (l.includes('retrain') || l.includes('train model')) result.intent = 'retrain'
  else if (l.includes('predict') || l.includes('batch')) result.intent = 'predictions'
  else if (l.includes('health') || l.includes('auc')) result.intent = 'health'
  else if (l.includes('chart') || l.includes('graph')) result.intent = 'chart'
  else if (l.includes('filter') || l.includes('available')) result.intent = 'filters'

  // ── Detect aggregation queries (branch/county ranking) ──────
  // e.g. "top 5 branches with high attrition", "which branch has highest risk"
  else if (
    (l.includes('branch') || l.includes('county')) &&
    (l.includes('top') || l.includes('highest') || l.includes('most') || l.includes('which'))  &&
    !l.includes('member') && !l.includes('customer')
  ) {
    result.intent = 'aggregation'
    result.params.group_by = l.includes('county') ? 'county' : 'branch_assignment'
  }

  // ── Detect tier ─────────────────────────────────────────────
  if (l.includes('high risk') || l.includes('at risk') || l.includes('high attrition') || l.includes('high propensity')) result.params.tier = 'High'
  else if (l.includes('medium')) result.params.tier = 'Medium'
  else if (l.includes('low risk')) result.params.tier = 'Low'

  // ── Detect branch name ──────────────────────────────────────
  const branches = ['hartford','cromwell','glastonbury','east hartford','north haven','new haven','newington','enfield']
  for (const b of branches) {
    if (l.includes(b)) {
      result.params.branch = b.split(' ').map(w => w[0].toUpperCase() + w.slice(1)).join(' ')
      break
    }
  }

  // ── Detect top_n ────────────────────────────────────────────
  const nm = text.match(/top\s+(\d+)/i) || text.match(/(\d+)\s+(?:customer|member|branch|county)/i)
  if (nm) result.params.top_n = parseInt(nm[1])

  // ── Detect min probability ──────────────────────────────────
  const pm = text.match(/above\s+([\d.]+)\s*%/i) || text.match(/more than\s+([\d.]+)\s*%/i)
  if (pm) result.params.min_prob = parseFloat(pm[1]) > 1 ? parseFloat(pm[1]) / 100 : parseFloat(pm[1])

  return result
}