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
        <div className="flex items-center gap-2">
          {data.pdf_url && (
            <a href={data.pdf_url} target="_blank" rel="noreferrer" className="btn btn-secondary text-xs">
              📄 PDF Report
            </a>
          )}
          {data.chart_url && <a href={data.chart_url} target="_blank" rel="noreferrer" className="btn btn-secondary text-xs">View Full</a>}
        </div>
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