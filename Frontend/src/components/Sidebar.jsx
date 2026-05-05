import { useQuery } from '@tanstack/react-query'
import { Search, Filter, BarChart2, Play, RefreshCw, Heart, FileText, GitMerge } from 'lucide-react'
import { clsx } from 'clsx'
import { getAvailableFilters } from '../api'
import { useStore } from '../store'
import { SectionLabel, Spinner } from './UI'
import MergeButton from './MergeButton'
import { ModelInfoButton } from './ModelInfoModal'

const MODELS = [
  { id: 'attrition',  label: 'Attrition Risk', auc: '1.00', color: 'bg-red-100 text-red-600' },
  { id: 'loan',       label: 'Loan Offers',     auc: '0.85', color: 'bg-blue-100 text-blue-600' },
  { id: 'propensity', label: 'Propensity',       auc: '0.96', color: 'bg-purple-100 text-purple-600' },
]

export default function Sidebar({ onAction, onModelInfo }) {
  const model        = useStore(s => s.model)
  const setModel     = useStore(s => s.setModel)
  const filters      = useStore(s => s.filters)
  const setFilter    = useStore(s => s.setFilter)
  const resetFilters = useStore(s => s.resetFilters)

  const { data: filterData, isLoading: filtersLoading } = useQuery({
    queryKey: ['filters', model],
    queryFn : () => getAvailableFilters(model),
    staleTime: 60000,
  })
  const f = filterData?.filters || {}

  return (
    <aside className="w-56 bg-white border-r border-gray-200 flex flex-col flex-shrink-0 overflow-y-auto">

      {/* Model selector */}
      <div className="p-3 border-b border-gray-100">
        <SectionLabel>Model</SectionLabel>
        <div className="flex flex-col gap-1">
          {MODELS.map(m => (
            <button key={m.id} onClick={() => setModel(m.id)}
              className={clsx(
                'flex items-center gap-2 px-2.5 py-2 rounded-md transition-all text-left border',
                model === m.id
                  ? 'bg-brand-50 border-brand-100 text-brand-800'
                  : 'border-transparent text-gray-600 hover:bg-gray-50'
              )}
            >
              <div className={clsx('w-5 h-5 rounded text-[9px] font-bold flex items-center justify-center flex-shrink-0', m.color)}>
                {m.id[0].toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium truncate">{m.label}</div>
              </div>
              <div className="text-[10px] font-mono text-green-600 font-medium">{m.auc}</div>
              <ModelInfoButton model={m.id} onClick={onModelInfo} />
            </button>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="p-3 border-b border-gray-100">
        <div className="flex items-center justify-between mb-1.5">
          <SectionLabel>Filters</SectionLabel>
          <button onClick={resetFilters} className="text-[10px] text-gray-400 hover:text-brand-600 transition-colors">
            Reset
          </button>
        </div>
        {filtersLoading && (
          <div className="flex items-center gap-2 text-xs text-gray-400 py-1">
            <Spinner size={10} /> Loading...
          </div>
        )}
        <div className="flex flex-col gap-2">
          <div>
            <div className="text-[10px] text-gray-400 mb-0.5">Risk Tier</div>
            <select className="select" value={filters.tier} onChange={e => setFilter('tier', e.target.value)}>
              <option value="">All Tiers</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
          <div>
            <div className="text-[10px] text-gray-400 mb-0.5">Branch</div>
            <select className="select" value={filters.branch} onChange={e => setFilter('branch', e.target.value)}>
              <option value="">All Branches</option>
              {(f.branch_assignment || []).map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          </div>
          <div>
            <div className="text-[10px] text-gray-400 mb-0.5">Income Band</div>
            <select className="select" value={filters.income_band} onChange={e => setFilter('income_band', e.target.value)}>
              <option value="">All Income</option>
              {(f.income_band || []).map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          </div>
          <div>
            <div className="text-[10px] text-gray-400 mb-0.5">Top N Members</div>
            <input type="number" className="input" value={filters.top_n} min={1} max={10000}
              onChange={e => setFilter('top_n', parseInt(e.target.value) || 20)} />
          </div>
          <div>
            <div className="text-[10px] text-gray-400 mb-0.5">Min Probability</div>
            <input type="number" className="input" placeholder="e.g. 0.7" value={filters.min_prob}
              step="0.1" min="0" max="1" onChange={e => setFilter('min_prob', e.target.value)} />
          </div>
        </div>
      </div>

      {/* Query actions */}
      <div className="p-3 border-b border-gray-100">
        <SectionLabel>Query</SectionLabel>
        <div className="flex flex-col gap-1">
          <button className="sidebar-btn active" onClick={() => onAction('smart_query')}>
            <Search size={13} /> Smart Query
          </button>
          <button className="sidebar-btn" onClick={() => onAction('filters')}>
            <Filter size={13} /> Available Filters
          </button>
          <button className="sidebar-btn" onClick={() => onAction('unified')}>
            <FileText size={13} /> Unified Report
          </button>
          <button className="sidebar-btn" onClick={() => onAction('chart')}>
            <BarChart2 size={13} /> Branch Chart
          </button>
        </div>
      </div>

      {/* Job actions */}
      <div className="p-3 border-b border-gray-100">
        <SectionLabel>Jobs</SectionLabel>
        <div className="flex flex-col gap-1">
          <button className="sidebar-btn" onClick={() => onAction('predictions')}>
            <Play size={13} /> Run Predictions
          </button>
          <button
            className="sidebar-btn text-red-500 hover:bg-red-50 hover:text-red-700"
            onClick={() => onAction('retrain')}
          >
            <RefreshCw size={13} /> Retrain Model
          </button>
          <button className="sidebar-btn" onClick={() => onAction('health')}>
            <Heart size={13} /> Model Health
          </button>
        </div>
      </div>

      {/* Merge section */}
      <div className="p-3">
        <SectionLabel>Master Data</SectionLabel>
        <MergeButton compact={true} />
      </div>

    </aside>
  )
}