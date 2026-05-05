import { useStore } from '../store'
import { StatCard } from './UI'

const MODEL_LABELS = {
  attrition: 'Attrition model',
  loan: 'Loan offers model',
  propensity: 'Propensity model',
}

export default function StatsBar() {
  const stats = useStore(s => s.stats)
  const model = useStore(s => s.model)
  return (
    <div className="flex bg-white border-b border-gray-200 flex-shrink-0">
      <StatCard label="Total Members" value={stats?.total_before_filter?.toLocaleString()} color="text-brand-700" sub={MODEL_LABELS[model]} />
      <StatCard label="Shown" value={stats?.total_returned?.toLocaleString()} color="text-gray-800" sub="After filters" />
      <StatCard label="High Risk" value={stats?.high?.toLocaleString()} color="text-red-600" sub="Priority action" />
      <StatCard label="Medium Risk" value={stats?.medium?.toLocaleString()} color="text-amber-600" sub="Monitor" />
      <StatCard label="Low Risk" value={stats?.low?.toLocaleString()} color="text-green-600" sub="Stable" />
    </div>
  )
}
