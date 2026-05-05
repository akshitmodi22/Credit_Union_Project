import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Download, Search, RefreshCw } from 'lucide-react'
import { smartQuery, getModelHealth } from '../api'
import { TierBadge, RiskBar, ShapReasons, Spinner } from '../components/UI'
import MergeButton from '../components/MergeButton'

const PROB_KEY = {
  attrition:  'attrition_probability',
  loan:       'loan_offer_score',
  propensity: 'propensity_probability',
  master:     'priority_score',
}
const TIER_KEY = {
  attrition:  'attrition_tier',
  loan:       'loan_offer_tier',
  propensity: 'propensity_tier',
  master:     'priority_action',
}

const TIER_OPTIONS = {
  attrition:  ['','High','Medium','Low'],
  loan:       ['','High','Medium','Low'],
  propensity: ['','High','Medium','Low'],
  master:     ['','Urgent Retention','Loan Offer','CD Offer','Monitor Closely','Standard'],
}

export default function Members() {
  const [model,    setModel]    = useState('attrition')
  const [tier,     setTier]     = useState('')
  const [topN,     setTopN]     = useState(100)
  const [search,   setSearch]   = useState('')
  const [expanded, setExpanded] = useState(null)

  const { data, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['members-full', model, tier, topN],
    queryFn:  () => smartQuery({ model, tier: tier||undefined, top_n: topN }),
    staleTime: 60000,
  })

  const members = (data?.top_members || []).filter(m =>
    !search || m.member_id?.toLowerCase().includes(search.toLowerCase())
  )

  const isMaster = model === 'master'

  const { data: healthData } = useQuery({
    queryKey: ['model-health-members'],
    queryFn: getModelHealth,
    staleTime: 60000,
  })

  const currentModelInfo = healthData?.models?.[model] || {}
  const masterInfo = healthData?.master || {}

  return (
    <div className="flex flex-col flex-1 overflow-hidden">

      {/* Model info strip */}
      <div className="bg-gray-900 px-5 py-1.5 flex items-center gap-5 text-[10px] font-mono flex-shrink-0">
        {isMaster ? (
          <>
            <span className="text-gray-400">★ Master View</span>
            <span className="text-gray-500">|</span>
            <span className="text-gray-400">Members: <span className="text-teal-400">{masterInfo.total_members?.toLocaleString() || '—'}</span></span>
            <span className="text-gray-400">Merged: <span className="text-teal-400">{masterInfo.merged_at || '—'}</span></span>
            <span className="text-gray-400">Models: <span className="text-gray-300">Attrition + Loan + Propensity</span></span>
          </>
        ) : (
          <>
            <span className="flex items-center gap-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${currentModelInfo.status === 'healthy' ? 'bg-green-400' : 'bg-amber-400'}`} />
              <span className="text-gray-300 capitalize">{model}</span>
            </span>
            <span className="text-gray-500">|</span>
            <span className="text-gray-400">Version: <span className="text-blue-400">v{currentModelInfo.version || '—'}</span></span>
            <span className="text-gray-400">AUC: <span className={currentModelInfo.auc >= 0.8 ? 'text-green-400' : 'text-amber-400'}>{currentModelInfo.auc || '—'}</span></span>
            <span className="text-gray-400">Trained: <span className="text-blue-400">{currentModelInfo.trained_on || '—'}</span></span>
            <span className="text-gray-400">Predicted: <span className="text-purple-400">{currentModelInfo.predicted_on || currentModelInfo.trained_on || '—'}</span></span>
          </>
        )}
      </div>

      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-5 py-3 flex items-center gap-3 flex-shrink-0 flex-wrap">
        <div className="text-sm font-semibold text-gray-800">All Members</div>

        <select className="h-8 px-2.5 bg-gray-50 border border-gray-200 rounded-md text-xs text-gray-700 outline-none"
          value={model} onChange={e => { setModel(e.target.value); setTier('') }}>
          {['attrition','loan','propensity','master'].map(m => (
            <option key={m} value={m}>
              {m === 'master' ? '★ Master (All Models)' : m.charAt(0).toUpperCase()+m.slice(1)}
            </option>
          ))}
        </select>

        <select className="h-8 px-2.5 bg-gray-50 border border-gray-200 rounded-md text-xs text-gray-700 outline-none"
          value={tier} onChange={e => setTier(e.target.value)}>
          {(TIER_OPTIONS[model] || TIER_OPTIONS.attrition).map(t =>
            <option key={t} value={t}>{t || (isMaster ? 'All Actions' : 'All Tiers')}</option>
          )}
        </select>

        <select className="h-8 px-2.5 bg-gray-50 border border-gray-200 rounded-md text-xs text-gray-700 outline-none"
          value={topN} onChange={e => setTopN(parseInt(e.target.value))}>
          {[50,100,250,500,1000,5000,10000].map(n => (
            <option key={n} value={n}>Top {n.toLocaleString()}</option>
          ))}
        </select>

        {/* Search */}
        <div className="flex items-center gap-1.5 bg-gray-50 border border-gray-200 rounded-md px-2.5 h-8 flex-1 max-w-xs">
          <Search size={12} className="text-gray-400" />
          <input type="text" placeholder="Search member ID..." value={search}
            onChange={e => setSearch(e.target.value)}
            className="flex-1 bg-transparent text-xs outline-none text-gray-700 placeholder:text-gray-400" />
        </div>

        <button onClick={() => refetch()} className="btn btn-ghost text-xs">
          <RefreshCw size={12} className={isFetching ? 'spin' : ''} /> Refresh
        </button>

        {data?.downloads?.excel_url && (
          <a href={data.downloads.excel_url} target="_blank" rel="noreferrer" className="btn btn-secondary text-xs">
            <Download size={12} /> Excel
          </a>
        )}
        {data?.downloads?.pdf_url && (
          <a href={data.downloads.pdf_url} target="_blank" rel="noreferrer" className="btn btn-secondary text-xs">
            <Download size={12} /> PDF
          </a>
        )}
      </div>

      {/* Merge bar */}
      <div className="bg-purple-50 border-b border-purple-100 px-5 py-2 flex items-center gap-3 flex-shrink-0">
        <div className="text-[11px] text-purple-700 font-medium">
          📊 Merge all 3 model predictions into a single master view:
        </div>
        <MergeButton compact={false} />
      </div>

      {/* Stats strip */}
      {data?.summary && (
        <div className="bg-white border-b border-gray-100 px-5 py-2 flex items-center gap-6 text-xs text-gray-500 flex-shrink-0 flex-wrap">
          <span>Total: <strong className="text-gray-800">{data.summary.total_before_filter?.toLocaleString()}</strong></span>
          <span>Shown: <strong className="text-gray-800">{members.length?.toLocaleString()}</strong></span>

          {isMaster ? (
            <>
              <span>Urgent: <strong className="text-red-600">{data.summary.urgent_retention?.toLocaleString()}</strong></span>
              <span>Loan Offer: <strong className="text-blue-600">{data.summary.loan_offer?.toLocaleString()}</strong></span>
              <span>CD Offer: <strong className="text-purple-600">{data.summary.cd_offer?.toLocaleString()}</strong></span>
              <span>Monitor: <strong className="text-amber-600">{data.summary.monitor_closely?.toLocaleString()}</strong></span>
              <span>Standard: <strong className="text-green-600">{data.summary.standard?.toLocaleString()}</strong></span>
            </>
          ) : (
            <>
              <span>High: <strong className="text-red-600">{data.summary.high?.toLocaleString()}</strong></span>
              <span>Medium: <strong className="text-amber-600">{data.summary.medium?.toLocaleString()}</strong></span>
              <span>Low: <strong className="text-green-600">{data.summary.low?.toLocaleString()}</strong></span>
            </>
          )}

          {data.model_info && (
            <span className="ml-auto font-mono text-[10px] text-gray-400">
              {isMaster
                ? `Merged: ${data.model_info.merged_at} · ${data.model_info.total_members?.toLocaleString()} members`
                : `v${data.model_info.version} · AUC ${data.model_info.auc} · ${data.model_info.trained_on}`
              }
            </span>
          )}
        </div>
      )}

      {/* Table */}
      <div className="flex-1 overflow-auto">
        {isLoading ? (
          <div className="flex items-center justify-center py-20 gap-3 text-sm text-gray-400">
            <Spinner /> Loading members...
          </div>
        ) : (
          <table className="w-full text-sm border-collapse">
            <thead className="sticky top-0 bg-white z-10">
              <tr className="border-b border-gray-200">
                {isMaster ? (
                  ['','Member ID','Action','Priority','Attrition','Loan','Propensity','Branch','Income Band','Life Stage'].map(h => (
                    <th key={h} className="text-left px-4 py-2.5 text-[10px] font-semibold text-gray-400 uppercase tracking-wide">{h}</th>
                  ))
                ) : (
                  ['','Member ID','Tier','Risk Score','Branch','Income Band','Life Stage','Top Reason'].map(h => (
                    <th key={h} className="text-left px-4 py-2.5 text-[10px] font-semibold text-gray-400 uppercase tracking-wide">{h}</th>
                  ))
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {members.map(m => {
                const prob = m[PROB_KEY[model]] ?? 0
                const mTier = m[TIER_KEY[model]]
                const isExp = expanded === m.member_id
                return (
                  <>
                    <tr key={m.member_id}
                      className="hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => setExpanded(isExp ? null : m.member_id)}
                    >
                      <td className="px-4 py-2.5 text-gray-300 text-xs">{isExp ? '▼' : '▶'}</td>
                      <td className="px-4 py-2.5 font-mono text-[11px] text-gray-600">{m.member_id}</td>

                      {isMaster ? (
                        <>
                          <td className="px-4 py-2.5"><TierBadge tier={mTier} /></td>
                          <td className="px-4 py-2.5 w-32"><RiskBar value={prob} /></td>
                          <td className="px-4 py-2.5 text-[10px] text-gray-500">{m.attrition_probability != null ? `${(m.attrition_probability*100).toFixed(1)}%` : '—'}</td>
                          <td className="px-4 py-2.5 text-[10px] text-gray-500">{m.loan_offer_score != null ? `${(m.loan_offer_score*100).toFixed(1)}%` : '—'}</td>
                          <td className="px-4 py-2.5 text-[10px] text-gray-500">{m.propensity_probability != null ? `${(m.propensity_probability*100).toFixed(1)}%` : '—'}</td>
                        </>
                      ) : (
                        <>
                          <td className="px-4 py-2.5"><TierBadge tier={mTier} /></td>
                          <td className="px-4 py-2.5 w-40"><RiskBar value={prob} /></td>
                        </>
                      )}

                      <td className="px-4 py-2.5 text-[11px] text-gray-600">{m.branch_assignment || '—'}</td>
                      <td className="px-4 py-2.5 text-[11px] text-gray-600">{m.income_band || '—'}</td>
                      <td className="px-4 py-2.5 text-[11px] text-gray-600">{m.life_stage || '—'}</td>

                      {!isMaster && (
                        <td className="px-4 py-2.5 text-[10px] text-gray-500 max-w-xs truncate">{m.shap_reason_1 || '—'}</td>
                      )}
                    </tr>
                    {isExp && (
                      <tr key={`${m.member_id}-exp`} className="bg-gray-50 border-b border-gray-200">
                        <td />
                        <td colSpan={isMaster ? 9 : 7} className="px-6 py-4">
                          <div className="text-[11px] font-semibold text-gray-700 mb-3">
                            {isMaster ? `All Model Reasons — ${m.member_id}` : `Top 5 Risk Drivers — ${m.member_id}`}
                          </div>
                          {isMaster ? (
                            <div className="grid grid-cols-3 gap-6 text-[10px]">
                              {[
                                { label: 'Attrition', color: 'text-red-600', prefix: 'attrition_shap' },
                                { label: 'Loan', color: 'text-blue-600', prefix: 'loan_shap' },
                                { label: 'Propensity', color: 'text-purple-600', prefix: 'propensity_shap' },
                              ].map(({ label, color, prefix }) => (
                                <div key={prefix}>
                                  <div className={`font-semibold ${color} mb-2`}>{label} — Top Reasons</div>
                                  <div className="flex flex-col gap-1">
                                    {[1,2,3,4,5].map(i => {
                                      const reason = m[`${prefix}_${i}`]
                                      if (!reason) return null
                                      const isIncrease = reason.includes('increases')
                                      return (
                                        <div key={i} className="flex items-center gap-1.5">
                                          <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[8px] font-bold ${
                                            i <= 2 ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-500'
                                          }`}>{i}</span>
                                          <span className="text-gray-600">{reason.split(' (')[0].replace(/_/g, ' ')}</span>
                                          <span className={`text-[9px] ${isIncrease ? 'text-red-500' : 'text-green-500'}`}>
                                            {isIncrease ? '↑' : '↓'}
                                          </span>
                                        </div>
                                      )
                                    })}
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="flex flex-col gap-1.5">
                              {[1,2,3,4,5].map(i => {
                                const reason = m[`shap_reason_${i}`]
                                if (!reason) return null
                                const isIncrease = reason.includes('increases')
                                const parts = reason.replace(/[()]/g, '').split(' ')
                                const featureName = parts.slice(0, -1).join(' ')
                                const direction = parts[parts.length - 1]
                                return (
                                  <div key={i} className="flex items-center gap-2 text-[11px]">
                                    <span className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold ${
                                      i === 1 ? 'bg-red-100 text-red-600' :
                                      i === 2 ? 'bg-orange-100 text-orange-600' :
                                      'bg-gray-100 text-gray-500'
                                    }`}>{i}</span>
                                    <span className="text-gray-700 font-medium">{featureName.replace(/_/g, ' ')}</span>
                                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                                      isIncrease ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'
                                    }`}>
                                      {isIncrease ? '↑ increases risk' : '↓ decreases risk'}
                                    </span>
                                  </div>
                                )
                              })}
                            </div>
                          )}
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