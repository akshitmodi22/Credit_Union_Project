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
