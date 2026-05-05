#!/bin/bash
# Run from Frontend folder:
# cd "/Users/akshitmodi/Downloads/CU code engine/Frontend"
# bash create_components.sh

echo "Creating all missing files..."

# ── src/components/UI.jsx ──────────────────────────────────────
cat > src/components/UI.jsx << 'JSEOF'
import { useEffect } from 'react'
import { clsx } from 'clsx'
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react'
import { useStore } from '../store'

export function Spinner({ size = 14, className }) {
  return (
    <div
      className={clsx('spin rounded-full border-2 border-gray-200 border-t-brand-600', className)}
      style={{ width: size, height: size }}
    />
  )
}

export function TierBadge({ tier }) {
  if (!tier) return <span className="text-gray-400">—</span>
  const cls = tier === 'High' ? 'badge-high' : tier === 'Medium' ? 'badge-medium' : 'badge-low'
  return <span className={cls}>{tier}</span>
}

export function RiskBar({ value }) {
  const pct = (value * 100).toFixed(1)
  const color = value >= 0.7 ? '#dc2626' : value >= 0.4 ? '#d97706' : '#16a34a'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="font-mono text-[10px] text-gray-500 w-9 text-right">{pct}%</span>
    </div>
  )
}

export function StatCard({ label, value, color = 'text-gray-900', sub }) {
  return (
    <div className="flex-1 bg-white border-r border-gray-200 last:border-r-0 px-5 py-3">
      <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">{label}</div>
      <div className={clsx('text-2xl font-semibold tabular-nums leading-none', color)}>{value ?? '—'}</div>
      {sub && <div className="text-[10px] text-gray-400 mt-0.5">{sub}</div>}
    </div>
  )
}

export function SectionLabel({ children }) {
  return (
    <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-1.5 px-1">
      {children}
    </div>
  )
}

export function ValidationRow({ validation }) {
  if (!validation) return null
  const checks = [{ key: 'count', label: 'Count' }, { key: 'sorted', label: 'Sorted' }, { key: 'no_nulls', label: 'No Nulls' }]
  return (
    <div className="flex gap-1.5 flex-wrap mt-2 pt-2 border-t border-gray-100">
      {checks.map(({ key, label }) => {
        const v = validation[key]
        if (!v) return null
        const pass = v.passed !== false
        return (
          <span key={key} className={clsx('inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium', pass ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700')}>
            {pass ? '✓' : '✗'} {label}
          </span>
        )
      })}
      <span className={clsx('inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold', validation.all_valid ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700')}>
        {validation.all_valid ? '✓ All Valid' : '✗ Issues'}
      </span>
    </div>
  )
}

export function DownloadRow({ downloads }) {
  if (!downloads?.excel_url && !downloads?.pdf_url) return null
  return (
    <div className="flex gap-2 mt-3 pt-3 border-t border-gray-100 items-center">
      {downloads.excel_url && (
        <a href={downloads.excel_url} target="_blank" rel="noreferrer" className="btn btn-secondary text-xs">📊 Excel Report</a>
      )}
      {downloads.pdf_url && (
        <a href={downloads.pdf_url} target="_blank" rel="noreferrer" className="btn btn-secondary text-xs">📄 PDF Report</a>
      )}
      <span className="text-[10px] text-gray-400 ml-auto">Expires in 24h</span>
    </div>
  )
}

function Toast({ toast }) {
  const removeToast = useStore(s => s.removeToast)
  useEffect(() => {
    const t = setTimeout(() => removeToast(toast.id), 3000)
    return () => clearTimeout(t)
  }, [toast.id, removeToast])
  const icons = { success: CheckCircle, error: AlertCircle, info: Info }
  const colors = { success: 'text-green-600', error: 'text-red-600', info: 'text-brand-600' }
  const Icon = icons[toast.type] || Info
  return (
    <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-lg shadow-sm px-3 py-2 text-sm fade-up">
      <Icon size={14} className={colors[toast.type] || colors.info} />
      <span className="text-gray-700">{toast.msg}</span>
      <button onClick={() => removeToast(toast.id)} className="ml-2 text-gray-400 hover:text-gray-600"><X size={12} /></button>
    </div>
  )
}

export function ToastContainer() {
  const toasts = useStore(s => s.toasts)
  return (
    <div className="fixed bottom-4 right-4 flex flex-col gap-2 z-50">
      {toasts.map(t => <Toast key={t.id} toast={t} />)}
    </div>
  )
}

export function LoadingCard({ message }) {
  return (
    <div className="card fade-up">
      <div className="flex items-center gap-3 px-4 py-4 text-sm text-gray-500">
        <Spinner />{message}
      </div>
    </div>
  )
}

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3 text-center">
      <div className="w-12 h-12 bg-brand-50 rounded-xl flex items-center justify-center">
        <span className="text-2xl">🏦</span>
      </div>
      <div className="text-base font-semibold text-gray-700">Credit Union Intelligence</div>
      <div className="text-sm text-gray-400 max-w-xs leading-relaxed">
        Select a model, apply filters, and run a query — or ask a question in the chat panel.
      </div>
    </div>
  )
}

export function ShapReasons({ member, count = 5 }) {
  const reasons = []
  for (let i = 1; i <= count; i++) {
    const r = member[`shap_reason_${i}`]
    if (r) reasons.push(r)
  }
  if (!reasons.length) return <span className="text-gray-400 text-xs">—</span>
  return (
    <div className="flex flex-col gap-0.5">
      {reasons.map((r, i) => (
        <div key={i} className="text-[10px] text-gray-500 flex items-start gap-1">
          <span className="text-gray-300 font-mono">{i + 1}.</span>
          <span>{r}</span>
        </div>
      ))}
    </div>
  )
}
JSEOF

# ── src/components/Topbar.jsx ──────────────────────────────────
cat > src/components/Topbar.jsx << 'JSEOF'
import { NavLink } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { LayoutDashboard, Users, Briefcase, Activity } from 'lucide-react'
import { clsx } from 'clsx'
import { getHealth } from '../api'
import { useStore } from '../store'

const NAV = [
  { to: '/',        label: 'Dashboard', icon: LayoutDashboard },
  { to: '/members', label: 'Members',   icon: Users },
  { to: '/jobs',    label: 'Jobs',      icon: Briefcase },
  { to: '/health',  label: 'Health',    icon: Activity },
]

export default function Topbar() {
  const setServerOnline = useStore(s => s.setServerOnline)
  useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const d = await getHealth()
      setServerOnline(d.status === 'ok')
      return d
    },
    refetchInterval: 30000,
  })
  const serverOnline = useStore(s => s.serverOnline)

  return (
    <header className="bg-white border-b border-gray-200 flex items-center px-5 gap-6 flex-shrink-0 z-10" style={{height:52}}>
      <div className="flex items-center gap-2 font-semibold text-sm text-gray-900 select-none">
        <div className="w-6 h-6 bg-brand-600 rounded-md flex items-center justify-center text-white text-[10px] font-bold">CU</div>
        Credit Union Intelligence
      </div>
      <nav className="flex items-center gap-0.5 flex-1">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === '/'}
            className={({ isActive }) => clsx(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all',
              isActive ? 'bg-brand-50 text-brand-700' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-100'
            )}
          >
            <Icon size={13} />{label}
          </NavLink>
        ))}
      </nav>
      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gray-50 border border-gray-200 text-[11px] font-mono text-gray-500">
        <div className={clsx('w-1.5 h-1.5 rounded-full', serverOnline ? 'bg-green-500' : 'bg-red-500')} />
        {serverOnline ? 'Online · 8080' : 'Offline'}
      </div>
    </header>
  )
}
JSEOF

# ── src/components/StatsBar.jsx ────────────────────────────────
cat > src/components/StatsBar.jsx << 'JSEOF'
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
JSEOF

# ── src/components/MemberTable.jsx ────────────────────────────
cat > src/components/MemberTable.jsx << 'JSEOF'
import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { TierBadge, RiskBar, ShapReasons, DownloadRow, ValidationRow } from './UI'

const PROB_KEY = { attrition: 'attrition_probability', loan: 'loan_offer_score', propensity: 'propensity_probability' }
const TIER_KEY = { attrition: 'attrition_tier', loan: 'loan_offer_tier', propensity: 'propensity_tier' }

function MemberRow({ member, model, expanded, onToggle }) {
  const prob = member[PROB_KEY[model]] ?? 0
  const tier = member[TIER_KEY[model]]
  return (
    <>
      <tr className="hover:bg-gray-50 cursor-pointer transition-colors" onClick={onToggle}>
        <td className="px-3 py-2 font-mono text-[11px] text-gray-600">
          <div className="flex items-center gap-1">
            {expanded ? <ChevronDown size={10} className="text-gray-400" /> : <ChevronRight size={10} className="text-gray-400" />}
            {member.member_id}
          </div>
        </td>
        <td className="px-3 py-2"><TierBadge tier={tier} /></td>
        <td className="px-3 py-2 w-36"><RiskBar value={prob} /></td>
        <td className="px-3 py-2 text-[10px] text-gray-500 max-w-[160px] truncate">{member.shap_reason_1 || '—'}</td>
        <td className="px-3 py-2 text-[11px] text-gray-500">{member.branch_assignment || '—'}</td>
        <td className="px-3 py-2 text-[11px] text-gray-500">{member.income_band || '—'}</td>
        <td className="px-3 py-2 text-[11px] text-gray-500">{member.life_stage || '—'}</td>
      </tr>
      {expanded && (
        <tr className="bg-brand-50">
          <td colSpan={7} className="px-6 py-3">
            <div className="text-[11px] font-semibold text-gray-600 mb-2">Top 5 SHAP Reasons — {member.member_id}</div>
            <ShapReasons member={member} count={5} />
          </td>
        </tr>
      )}
    </>
  )
}

export default function MemberTable({ data, model }) {
  const [expandedId, setExpandedId] = useState(null)
  const members = data?.top_members || []
  if (!members.length) return <div className="text-center py-10 text-sm text-gray-400">No members found.</div>
  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-gray-200">
              {['Member ID','Tier','Risk Score','Top Reason','Branch','Income','Life Stage'].map(h => (
                <th key={h} className="text-left px-3 py-2 text-[10px] font-semibold text-gray-400 uppercase tracking-wide">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {members.map(m => (
              <MemberRow key={m.member_id} member={m} model={model}
                expanded={expandedId === m.member_id}
                onToggle={() => setExpandedId(prev => prev === m.member_id ? null : m.member_id)}
              />
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-3">
        <ValidationRow validation={data?.validation} />
        <DownloadRow downloads={data?.downloads} />
      </div>
      <div className="px-3 pt-2 pb-1">
        <p className="text-[10px] text-gray-400">Click any row to expand top 5 SHAP reasons</p>
      </div>
    </div>
  )
}
JSEOF

# ── src/components/Sidebar.jsx ─────────────────────────────────
cat > src/components/Sidebar.jsx << 'JSEOF'
import { useQuery } from '@tanstack/react-query'
import { Search, Filter, BarChart2, Play, RefreshCw, Heart, FileText } from 'lucide-react'
import { clsx } from 'clsx'
import { getAvailableFilters } from '../api'
import { useStore } from '../store'
import { SectionLabel, Spinner } from './UI'

const MODELS = [
  { id: 'attrition',  label: 'Attrition Risk',  auc: '1.00', color: 'bg-red-100 text-red-600' },
  { id: 'loan',       label: 'Loan Offers',      auc: '0.85', color: 'bg-blue-100 text-blue-600' },
  { id: 'propensity', label: 'Propensity',        auc: '0.96', color: 'bg-purple-100 text-purple-600' },
]

export default function Sidebar({ onAction }) {
  const model = useStore(s => s.model)
  const setModel = useStore(s => s.setModel)
  const filters = useStore(s => s.filters)
  const setFilter = useStore(s => s.setFilter)
  const resetFilters = useStore(s => s.resetFilters)

  const { data: filterData, isLoading: filtersLoading } = useQuery({
    queryKey: ['filters', model],
    queryFn: () => getAvailableFilters(model),
    staleTime: 60000,
  })
  const f = filterData?.filters || {}

  return (
    <aside className="w-56 bg-white border-r border-gray-200 flex flex-col flex-shrink-0 overflow-y-auto">
      <div className="p-3 border-b border-gray-100">
        <SectionLabel>Model</SectionLabel>
        <div className="flex flex-col gap-1">
          {MODELS.map(m => (
            <button key={m.id} onClick={() => setModel(m.id)}
              className={clsx('flex items-center gap-2 px-2.5 py-2 rounded-md transition-all text-left border',
                model === m.id ? 'bg-brand-50 border-brand-100 text-brand-800' : 'border-transparent text-gray-600 hover:bg-gray-50'
              )}
            >
              <div className={clsx('w-5 h-5 rounded text-[9px] font-bold flex items-center justify-center flex-shrink-0', m.color)}>
                {m.id[0].toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium truncate">{m.label}</div>
              </div>
              <div className="text-[10px] font-mono text-green-600 font-medium">{m.auc}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="p-3 border-b border-gray-100">
        <div className="flex items-center justify-between mb-1.5">
          <SectionLabel>Filters</SectionLabel>
          <button onClick={resetFilters} className="text-[10px] text-gray-400 hover:text-brand-600 transition-colors">Reset</button>
        </div>
        {filtersLoading && <div className="flex items-center gap-2 text-xs text-gray-400 py-1"><Spinner size={10} /> Loading...</div>}
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

      <div className="p-3 border-b border-gray-100">
        <SectionLabel>Query</SectionLabel>
        <div className="flex flex-col gap-1">
          <button className="sidebar-btn active" onClick={() => onAction('smart_query')}><Search size={13} /> Smart Query</button>
          <button className="sidebar-btn" onClick={() => onAction('filters')}><Filter size={13} /> Available Filters</button>
          <button className="sidebar-btn" onClick={() => onAction('unified')}><FileText size={13} /> Unified Report</button>
          <button className="sidebar-btn" onClick={() => onAction('chart')}><BarChart2 size={13} /> Branch Chart</button>
        </div>
      </div>

      <div className="p-3">
        <SectionLabel>Jobs</SectionLabel>
        <div className="flex flex-col gap-1">
          <button className="sidebar-btn" onClick={() => onAction('predictions')}><Play size={13} /> Run Predictions</button>
          <button className="sidebar-btn text-red-500 hover:bg-red-50 hover:text-red-700" onClick={() => onAction('retrain')}><RefreshCw size={13} /> Retrain Model</button>
          <button className="sidebar-btn" onClick={() => onAction('health')}><Heart size={13} /> Model Health</button>
        </div>
      </div>
    </aside>
  )
}
JSEOF

# ── src/components/ResultCards.jsx ────────────────────────────
cat > src/components/ResultCards.jsx << 'JSEOF'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { RiskBar, DownloadRow } from './UI'
import MemberTable from './MemberTable'

export function SmartQueryCard({ data, model }) {
  const s = data.summary || {}
  const f = data.filters_used || {}
  const subtitle = [f.branch, f.tier, `Top ${s.total_returned || 0}`].filter(Boolean).join(' · ')
  return (
    <div className="card fade-up">
      <div className="card-header">
        <div className="card-title">🔍 Smart Query <span className="text-gray-400 font-normal text-xs">{subtitle}</span></div>
        <span className="text-[10px] text-gray-400 font-mono">{s.total_before_filter?.toLocaleString()} total · {s.total_returned?.toLocaleString()} shown</span>
      </div>
      <MemberTable data={data} model={model} />
    </div>
  )
}

export function HealthCard({ data }) {
  const models = data.models || {}
  return (
    <div className="card fade-up">
      <div className="card-header">
        <div className="card-title">💊 Model Health</div>
        <span className="text-[10px] text-gray-400 font-mono">{data.checked}</span>
      </div>
      <div className="divide-y divide-gray-100">
        {Object.entries(models).map(([name, info]) => {
          const ok = info.status === 'healthy'
          return (
            <div key={name} className="flex items-center justify-between px-4 py-3">
              <div>
                <div className="text-sm font-semibold capitalize text-gray-800">{name}</div>
                <div className="text-[11px] text-gray-400 font-mono mt-0.5">v{info.version} · {info.trained_on}</div>
              </div>
              <div className="text-right">
                <div className={`text-xl font-bold tabular-nums ${ok ? 'text-green-600' : 'text-red-600'}`}>{info.auc}</div>
                <div className={`text-[10px] font-medium ${ok ? 'text-green-500' : 'text-red-500'}`}>{info.status}</div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export function JobCard({ data, title }) {
  const results = data.results || {}
  return (
    <div className="card fade-up">
      <div className="card-header">
        <div className="card-title">⚡ {title}</div>
        <span className="text-[10px] text-gray-400">{new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</span>
      </div>
      <div className="p-3 flex flex-col gap-2">
        {Object.entries(results).map(([model, res]) => {
          const ok = res.state === 'Completed'
          return (
            <div key={model} className={`rounded-lg p-3 border text-sm ${ok ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
              <div className="font-semibold capitalize mb-1 text-gray-800">{model} — <span className={ok ? 'text-green-700' : 'text-red-700'}>{res.state}</span></div>
              <div className="text-[11px] text-gray-500 line-clamp-2">{res.summary}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export function ChartCard({ data }) {
  const breakdown = data.breakdown || {}
  const chartData = Object.entries(breakdown)
    .map(([name, value]) => ({ name: name.length > 12 ? name.slice(0, 12) + '…' : name, value }))
    .sort((a, b) => b.value - a.value)
  return (
    <div className="card fade-up">
      <div className="card-header">
        <div className="card-title">📈 Branch Chart <span className="text-gray-400 font-normal text-xs">Top: {data.top_group} ({data.top_count})</span></div>
        {data.chart_url && <a href={data.chart_url} target="_blank" rel="noreferrer" className="btn btn-secondary text-xs">View Full</a>}
      </div>
      <div className="p-4">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData} margin={{ top: 4, right: 8, left: -20, bottom: 40 }}>
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#9ca3af' }} angle={-35} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} />
            <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e5e7eb' }} cursor={{ fill: '#f9fafb' }} />
            <Bar dataKey="value" radius={[3, 3, 0, 0]}>
              {chartData.map((_, i) => <Cell key={i} fill={i === 0 ? '#387ED1' : '#93c5fd'} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export function UnifiedCard({ data }) {
  const top = data.top_priority || []
  const dl = data.downloads || {}
  return (
    <div className="card fade-up">
      <div className="card-header">
        <div className="card-title">📊 Unified Report <span className="text-gray-400 font-normal text-xs">{data.total_members?.toLocaleString()} members · {data.priority_actions} priority</span></div>
        <span className="text-[10px] text-gray-400">{new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-gray-200">
              {['Member ID','Attrition','Loan','Propensity','Action'].map(h => (
                <th key={h} className="text-left px-3 py-2 text-[10px] font-semibold text-gray-400 uppercase tracking-wide">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {top.map(m => (
              <tr key={m.member_id} className="hover:bg-gray-50">
                <td className="px-3 py-2 font-mono text-[11px] text-gray-600">{m.member_id}</td>
                <td className="px-3 py-2"><RiskBar value={m.attrition_probability || 0} /></td>
                <td className="px-3 py-2"><RiskBar value={m.loan_offer_score || 0} /></td>
                <td className="px-3 py-2"><RiskBar value={m.propensity_probability || 0} /></td>
                <td className="px-3 py-2 text-[10px] text-red-600 font-medium">{m.priority_action || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {dl.excel_url && <div className="px-3 pb-3"><DownloadRow downloads={dl} /></div>}
    </div>
  )
}

export function FiltersCard({ data }) {
  const filters = data.filters || {}
  return (
    <div className="card fade-up">
      <div className="card-header">
        <div className="card-title">🗂 Available Filters</div>
        <span className="text-[10px] text-gray-500 capitalize">{data.model}</span>
      </div>
      <div className="p-4 grid grid-cols-2 gap-4">
        {Object.entries(filters).map(([key, vals]) => (
          <div key={key}>
            <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1.5">{key.replace(/_/g, ' ')}</div>
            <div className="flex flex-wrap gap-1">
              {vals.slice(0, 8).map(v => <span key={v} className="px-2 py-0.5 bg-gray-100 border border-gray-200 rounded text-[10px] font-mono text-gray-600">{v}</span>)}
              {vals.length > 8 && <span className="px-2 py-0.5 text-[10px] text-gray-400">+{vals.length - 8}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
JSEOF

# ── src/pages/Members.jsx ──────────────────────────────────────
cat > src/pages/Members.jsx << 'JSEOF'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Download, Search, RefreshCw } from 'lucide-react'
import { smartQuery } from '../api'
import { TierBadge, RiskBar, ShapReasons, Spinner } from '../components/UI'

const PROB_KEY = { attrition: 'attrition_probability', loan: 'loan_offer_score', propensity: 'propensity_probability' }
const TIER_KEY = { attrition: 'attrition_tier', loan: 'loan_offer_tier', propensity: 'propensity_tier' }

export default function Members() {
  const [model, setModel] = useState('attrition')
  const [tier, setTier] = useState('')
  const [topN, setTopN] = useState(100)
  const [search, setSearch] = useState('')
  const [expanded, setExpanded] = useState(null)

  const { data, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['members-full', model, tier, topN],
    queryFn: () => smartQuery({ model, tier: tier||undefined, top_n: topN }),
    staleTime: 60000,
  })

  const members = (data?.top_members || []).filter(m =>
    !search || m.member_id?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      <div className="bg-white border-b border-gray-200 px-5 py-3 flex items-center gap-3 flex-shrink-0 flex-wrap">
        <div className="text-sm font-semibold text-gray-800">All Members</div>
        <select className="h-8 px-2.5 bg-gray-50 border border-gray-200 rounded-md text-xs text-gray-700 outline-none focus:border-brand-400" value={model} onChange={e => setModel(e.target.value)}>
          {['attrition','loan','propensity'].map(m => <option key={m} value={m} className="capitalize">{m.charAt(0).toUpperCase()+m.slice(1)}</option>)}
        </select>
        <select className="h-8 px-2.5 bg-gray-50 border border-gray-200 rounded-md text-xs text-gray-700 outline-none focus:border-brand-400" value={tier} onChange={e => setTier(e.target.value)}>
          {['','High','Medium','Low'].map(t => <option key={t} value={t}>{t || 'All Tiers'}</option>)}
        </select>
        <select className="h-8 px-2.5 bg-gray-50 border border-gray-200 rounded-md text-xs text-gray-700 outline-none focus:border-brand-400" value={topN} onChange={e => setTopN(parseInt(e.target.value))}>
          {[50,100,250,500,1000,5000,10000].map(n => <option key={n} value={n}>Top {n.toLocaleString()}</option>)}
        </select>
        <div className="flex items-center gap-1.5 bg-gray-50 border border-gray-200 rounded-md px-2.5 h-8 flex-1 max-w-xs">
          <Search size={12} className="text-gray-400" />
          <input type="text" placeholder="Search member ID..." value={search} onChange={e => setSearch(e.target.value)} className="flex-1 bg-transparent text-xs outline-none text-gray-700 placeholder:text-gray-400" />
        </div>
        <button onClick={() => refetch()} className="btn btn-ghost text-xs"><RefreshCw size={12} className={isFetching ? 'spin' : ''} /> Refresh</button>
        {data?.downloads?.excel_url && <a href={data.downloads.excel_url} target="_blank" rel="noreferrer" className="btn btn-secondary text-xs"><Download size={12} /> Excel</a>}
        {data?.downloads?.pdf_url && <a href={data.downloads.pdf_url} target="_blank" rel="noreferrer" className="btn btn-secondary text-xs"><Download size={12} /> PDF</a>}
      </div>

      {data?.summary && (
        <div className="bg-white border-b border-gray-100 px-5 py-2 flex items-center gap-6 text-xs text-gray-500 flex-shrink-0">
          <span>Total: <strong className="text-gray-800">{data.summary.total_before_filter?.toLocaleString()}</strong></span>
          <span>Shown: <strong className="text-gray-800">{members.length?.toLocaleString()}</strong></span>
          <span>High: <strong className="text-red-600">{data.summary.high?.toLocaleString()}</strong></span>
          <span>Medium: <strong className="text-amber-600">{data.summary.medium?.toLocaleString()}</strong></span>
          <span>Low: <strong className="text-green-600">{data.summary.low?.toLocaleString()}</strong></span>
          {data.model_info && <span className="ml-auto font-mono text-[10px] text-gray-400">v{data.model_info.version} · AUC {data.model_info.auc} · {data.model_info.trained_on}</span>}
        </div>
      )}

      <div className="flex-1 overflow-auto">
        {isLoading ? (
          <div className="flex items-center justify-center py-20 gap-3 text-sm text-gray-400"><Spinner /> Loading members...</div>
        ) : (
          <table className="w-full text-sm border-collapse">
            <thead className="sticky top-0 bg-white z-10">
              <tr className="border-b border-gray-200">
                {['','Member ID','Tier','Risk Score','Branch','Income Band','Life Stage','Top Reason'].map(h => (
                  <th key={h} className="text-left px-4 py-2.5 text-[10px] font-semibold text-gray-400 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {members.map(m => {
                const prob = m[PROB_KEY[model]] ?? 0
                const mTier = m[TIER_KEY[model]]
                const isExp = expanded === m.member_id
                return (
                  <>
                    <tr key={m.member_id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setExpanded(isExp ? null : m.member_id)}>
                      <td className="px-4 py-2.5 text-gray-300 text-xs">{isExp ? '▼' : '▶'}</td>
                      <td className="px-4 py-2.5 font-mono text-[11px] text-gray-600">{m.member_id}</td>
                      <td className="px-4 py-2.5"><TierBadge tier={mTier} /></td>
                      <td className="px-4 py-2.5 w-40"><RiskBar value={prob} /></td>
                      <td className="px-4 py-2.5 text-[11px] text-gray-600">{m.branch_assignment || '—'}</td>
                      <td className="px-4 py-2.5 text-[11px] text-gray-600">{m.income_band || '—'}</td>
                      <td className="px-4 py-2.5 text-[11px] text-gray-600">{m.life_stage || '—'}</td>
                      <td className="px-4 py-2.5 text-[10px] text-gray-500 max-w-xs truncate">{m.shap_reason_1 || '—'}</td>
                    </tr>
                    {isExp && (
                      <tr key={`${m.member_id}-exp`} className="bg-brand-50">
                        <td />
                        <td colSpan={7} className="px-6 py-3">
                          <div className="text-[11px] font-semibold text-gray-700 mb-2">Top 5 SHAP Reasons — {m.member_id}</div>
                          <ShapReasons member={m} count={5} />
                        </td>
                      </tr>
                    )}
                  </>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
JSEOF

# ── src/pages/Jobs.jsx ─────────────────────────────────────────
cat > src/pages/Jobs.jsx << 'JSEOF'
import { useState } from 'react'
import { Play, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react'
import { runPredictions, runRetrain } from '../api'
import { useStore } from '../store'
import { Spinner } from '../components/UI'

const MODELS = ['attrition', 'loan', 'propensity']

export default function Jobs() {
  const addToast = useStore(s => s.addToast)
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState({})

  async function trigger(model, type) {
    const key = `${model}_${type}`
    setLoading(prev => ({ ...prev, [key]: true }))
    const startTime = new Date()
    try {
      const fn = type === 'predict' ? runPredictions : runRetrain
      const data = await fn(model)
      const state = data.results?.[model]?.state || 'Unknown'
      setRuns(prev => [{
        id: Date.now(), model, type, state,
        summary: data.results?.[model]?.summary || '',
        started: startTime.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}),
        duration: `${Math.round((new Date() - startTime) / 1000)}s`,
      }, ...prev])
      addToast(`${type === 'predict' ? 'Predictions' : 'Retrain'} for ${model}: ${state}`, state === 'Completed' ? 'success' : 'error')
    } catch (e) {
      setRuns(prev => [{ id: Date.now(), model, type, state: 'Error', summary: e.message, started: startTime.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}), duration: '—' }, ...prev])
      addToast(`Error: ${e.message}`, 'error')
    }
    setLoading(prev => ({ ...prev, [key]: false }))
  }

  function StateIcon({ state }) {
    if (state === 'Completed') return <CheckCircle size={14} className="text-green-500" />
    if (state === 'Failed' || state === 'Error') return <XCircle size={14} className="text-red-500" />
    return <Clock size={14} className="text-amber-500" />
  }

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      <div className="bg-white border-b border-gray-200 px-5 py-3 flex-shrink-0">
        <div className="text-sm font-semibold text-gray-800">Jobs</div>
        <div className="text-xs text-gray-400 mt-0.5">Trigger batch predictions and model retraining</div>
      </div>
      <div className="flex-1 overflow-y-auto p-5">
        <div className="max-w-3xl mx-auto flex flex-col gap-6">
          <div>
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Trigger Jobs</div>
            <div className="grid grid-cols-3 gap-3">
              {MODELS.map(model => (
                <div key={model} className="bg-white border border-gray-200 rounded-xl p-4">
                  <div className="text-sm font-semibold capitalize text-gray-800 mb-3">{model}</div>
                  <div className="flex flex-col gap-2">
                    <button onClick={() => trigger(model, 'predict')} disabled={loading[`${model}_predict`]} className="btn btn-primary text-xs justify-center">
                      {loading[`${model}_predict`] ? <><Spinner size={11} /> Running...</> : <><Play size={11} /> Run Predictions</>}
                    </button>
                    <button onClick={() => { if (window.confirm(`Retrain ${model}?`)) trigger(model, 'train') }} disabled={loading[`${model}_train`]} className="btn btn-danger text-xs justify-center">
                      {loading[`${model}_train`] ? <><Spinner size={11} /> Running...</> : <><RefreshCw size={11} /> Retrain</>}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
          {runs.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Run History</div>
              <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50">
                      {['Status','Model','Type','Started','Duration','Summary'].map(h => (
                        <th key={h} className="text-left px-4 py-2.5 text-[10px] font-semibold text-gray-400 uppercase tracking-wide">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {runs.map(run => (
                      <tr key={run.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3"><StateIcon state={run.state} /></td>
                        <td className="px-4 py-3 text-xs font-medium capitalize text-gray-800">{run.model}</td>
                        <td className="px-4 py-3"><span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-medium ${run.type === 'predict' ? 'bg-blue-50 text-blue-700' : 'bg-orange-50 text-orange-700'}`}>{run.type === 'predict' ? 'Predictions' : 'Retrain'}</span></td>
                        <td className="px-4 py-3 text-[11px] text-gray-500 font-mono">{run.started}</td>
                        <td className="px-4 py-3 text-[11px] text-gray-500 font-mono">{run.duration}</td>
                        <td className="px-4 py-3 text-[10px] text-gray-500 max-w-xs truncate">{run.summary?.slice(0, 80)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          {runs.length === 0 && <div className="text-center py-12 text-sm text-gray-400">No jobs run yet.</div>}
        </div>
      </div>
    </div>
  )
}
JSEOF

# ── src/pages/Health.jsx ───────────────────────────────────────
cat > src/pages/Health.jsx << 'JSEOF'
import { useQuery } from '@tanstack/react-query'
import { RefreshCw } from 'lucide-react'
import { getModelHealth } from '../api'
import { Spinner } from '../components/UI'

export default function Health() {
  const { data, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['model-health'],
    queryFn: getModelHealth,
    refetchInterval: 60000,
  })
  const models = data?.models || {}
  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      <div className="bg-white border-b border-gray-200 px-5 py-3 flex items-center justify-between flex-shrink-0">
        <div>
          <div className="text-sm font-semibold text-gray-800">Model Health</div>
          {data?.checked && <div className="text-xs text-gray-400 mt-0.5 font-mono">Last checked: {data.checked}</div>}
        </div>
        <button onClick={() => refetch()} className="btn btn-secondary text-xs"><RefreshCw size={12} className={isFetching ? 'spin' : ''} /> Refresh</button>
      </div>
      <div className="flex-1 overflow-y-auto p-5">
        <div className="max-w-2xl mx-auto">
          {isLoading ? (
            <div className="flex items-center justify-center py-20 gap-3 text-sm text-gray-400"><Spinner /> Checking models...</div>
          ) : (
            <div className="flex flex-col gap-4">
              {Object.entries(models).map(([name, info]) => {
                const ok = info.status === 'healthy'
                return (
                  <div key={name} className={`bg-white border rounded-xl overflow-hidden ${ok ? 'border-gray-200' : 'border-red-200'}`}>
                    <div className={`flex items-center justify-between px-5 py-4 border-b ${ok ? 'border-gray-100 bg-gray-50' : 'border-red-100 bg-red-50'}`}>
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${ok ? 'bg-green-500' : 'bg-red-500'}`} />
                        <div className="text-sm font-semibold capitalize text-gray-800">{name} Model</div>
                        <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-semibold ${ok ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>{info.status}</span>
                      </div>
                      <div className={`text-3xl font-bold tabular-nums ${ok ? 'text-green-600' : 'text-red-600'}`}>{info.auc}<span className="text-sm font-normal text-gray-400 ml-1">AUC</span></div>
                    </div>
                    <div className="px-5 py-4 grid grid-cols-3 gap-4">
                      <div><div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">Version</div><div className="text-sm font-semibold text-gray-800">v{info.version}</div></div>
                      <div><div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">Trained On</div><div className="text-sm font-semibold text-gray-800 font-mono">{info.trained_on}</div></div>
                      <div><div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">Status</div><div className={`text-sm font-semibold ${ok ? 'text-green-600' : 'text-red-600'}`}>{ok ? '✓ Healthy' : '✗ Degraded'}</div></div>
                    </div>
                    <div className="px-5 pb-4">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${ok ? 'bg-green-500' : 'bg-red-500'}`} style={{ width: `${info.auc * 100}%` }} />
                        </div>
                        <div className="text-xs font-mono text-gray-600 w-10 text-right">{(info.auc * 100).toFixed(1)}%</div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
JSEOF

echo ""
echo "✓ All files created successfully!"
echo ""
echo "Now run: npm run dev"
