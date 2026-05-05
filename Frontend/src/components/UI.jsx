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
