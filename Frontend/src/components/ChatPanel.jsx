import { useState, useRef, useEffect } from 'react'
import { Send, Bot } from 'lucide-react'
import { clsx } from 'clsx'
import { parseNL } from '../hooks/useNLP'
import { useStore } from '../store'
import { smartQuery, runPredictions, runRetrain, getModelHealth, getUnifiedReport, generateChart, getAvailableFilters } from '../api'

const SUGGESTIONS = [
  'Top 1000 high risk attrition members',
  'Hartford branch high propensity report',
  'Run attrition predictions',
  'Check model health status',
  'Show loan offer chart by branch',
  'Top 500 high risk members above 80% probability',
]

function Msg({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={clsx('flex flex-col gap-1', isUser ? 'items-end' : 'items-start')}>
      <div
        className={clsx(
          'max-w-[86%] px-3 py-2 rounded-xl text-[12px] leading-relaxed',
          isUser
            ? 'bg-brand-600 text-white rounded-br-sm'
            : 'bg-gray-100 text-gray-800 border border-gray-200 rounded-bl-sm'
        )}
        dangerouslySetInnerHTML={{ __html: msg.text }}
      />
      <div className="text-[9px] text-gray-400 font-mono">{msg.time}</div>
    </div>
  )
}

function Thinking() {
  return (
    <div className="flex items-center gap-1 px-3 py-2 bg-gray-100 border border-gray-200 rounded-xl rounded-bl-sm w-fit">
      {[0, 1, 2].map(i => (
        <div
          key={i}
          className="w-1.5 h-1.5 bg-brand-400 rounded-full"
          style={{ animation: `bounce 1.1s infinite ${i * 0.18}s` }}
        />
      ))}
    </div>
  )
}

export default function ChatPanel({ onResult }) {
  const model = useStore(s => s.model)
  const addToast = useStore(s => s.addToast)
  const [msgs, setMsgs] = useState([
    {
      role: 'ai',
      text: '👋 Hello! Ask me anything about member risk in natural language.<br/>Try: <em>"top 1000 high risk attrition members from Hartford"</em>',
      time: now(),
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  function now() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [msgs, loading])

  function addMsg(role, text) {
    setMsgs(prev => [...prev, { role, text, time: now() }])
  }

  async function send() {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    addMsg('user', text)
    setLoading(true)

    const q = parseNL(text, model)
    try {
      let reply = ''

      if (q.intent === 'smart_query') {
        const params = { model: q.model, top_n: q.params.top_n || 20, ...q.params }
        const d = await smartQuery(params)
        if (d.status === 'success') {
          onResult({ type: 'smart_query', data: d, model: q.model })
          const s = d.summary
          const f = d.filters_used
          reply = `Found <strong>${s.total_returned?.toLocaleString()}</strong> members`
          if (f.branch) reply += ` in <strong>${f.branch}</strong>`
          if (f.tier) reply += ` · <strong>${f.tier}</strong> risk`
          reply += `<br/>High: ${s.high} · Medium: ${s.medium} · Low: ${s.low}`
          if (d.validation?.all_valid) reply += `<br/><span style="color:#16a34a">✓ All validation passed</span>`
          if (d.downloads?.excel_url) reply += `<br/>📥 Reports ready — check main panel`
        } else {
          reply = '⚠️ No members found. Try different filters.'
        }
      }

      else if (q.intent === 'health') {
        const d = await getModelHealth()
        onResult({ type: 'health', data: d })
        reply = 'Model health:<br/>' + Object.entries(d.models || {}).map(([n, i]) =>
          `${i.status === 'healthy' ? '✅' : '⚠️'} <strong>${n}</strong>: v${i.version} · AUC ${i.auc}`
        ).join('<br/>')
      }

      else if (q.intent === 'predictions') {
        const d = await runPredictions(q.model)
        onResult({ type: 'job', data: d, title: 'Batch Predictions' })
        const state = d.results?.[q.model]?.state || 'Unknown'
        reply = `Predictions for <strong>${q.model}</strong>: <strong>${state}</strong>`
        addToast(`Predictions triggered for ${q.model}`, 'success')
      }

      else if (q.intent === 'retrain') {
        const d = await runRetrain(q.model)
        onResult({ type: 'job', data: d, title: 'Model Retraining' })
        const state = d.results?.[q.model]?.state || 'Unknown'
        reply = `Retrain <strong>${q.model}</strong>: <strong>${state}</strong>`
        addToast(`Retrain triggered for ${q.model}`, 'success')
      }

      else if (q.intent === 'unified') {
        const d = await getUnifiedReport(q.params.branch)
        onResult({ type: 'unified', data: d })
        reply = `Unified report: <strong>${d.total_members?.toLocaleString()}</strong> members · <strong>${d.priority_actions}</strong> priority`
      }

      else if (q.intent === 'aggregation') {
        const groupBy = q.params.group_by || 'branch_assignment'
        const d = await generateChart({ model: q.model, group_by: groupBy, tier: q.params.tier || 'High' })
        onResult({ type: 'chart', data: d })
        const label = groupBy === 'county' ? 'County' : 'Branch'
        const breakdown = d.breakdown || {}
        const entries = Object.entries(breakdown).sort((a, b) => b[1] - a[1]).slice(0, q.params.top_n || 10)
        reply = `<strong>Top ${entries.length} ${label}s — ${q.params.tier || 'High'} Risk ${q.model}</strong><br/>`
        reply += entries.map(([name, count], i) =>
          `${i + 1}. <strong>${name}</strong>: ${count} members`
        ).join('<br/>')
        if (d.chart_url) reply += `<br/><br/>📊 Chart image available — check main panel`
        if (d.pdf_url) reply += `<br/>📄 <a href="${d.pdf_url}" target="_blank" style="color:#4F46E5;text-decoration:underline">Download PDF Report</a>`
      }

      else if (q.intent === 'chart') {
        const d = await generateChart({ model: q.model, tier: q.params.tier || 'High' })
        onResult({ type: 'chart', data: d })
        reply = `Branch chart for <strong>${q.model}</strong>. Top: <strong>${d.top_group}</strong> (${d.top_count})`
        if (d.pdf_url) reply += `<br/>📄 <a href="${d.pdf_url}" target="_blank" style="color:#4F46E5;text-decoration:underline">Download PDF Report</a>`
      }

      else if (q.intent === 'filters') {
        const d = await getAvailableFilters(q.model)
        onResult({ type: 'filters', data: d })
        reply = `Filter options loaded for <strong>${q.model}</strong> — see main panel.`
      }

      addMsg('ai', reply)
    } catch (e) {
      addMsg('ai', `❌ Error: ${e.message}<br/><small>Make sure server is running on port 8080</small>`)
    }

    setLoading(false)
  }

  return (
    <div className="w-80 border-l border-gray-200 bg-white flex flex-col flex-shrink-0">

      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-200 flex-shrink-0">
        <div className="w-7 h-7 bg-brand-600 rounded-lg flex items-center justify-center">
          <Bot size={14} className="text-white" />
        </div>
        <div>
          <div className="text-sm font-semibold text-gray-800">AI Assistant</div>
          <div className="text-[10px] text-gray-400">Natural language queries</div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-3 py-3 flex flex-col gap-2">
        {msgs.map((m, i) => <Msg key={i} msg={m} />)}
        {loading && (
          <div className="flex flex-col items-start gap-1">
            <Thinking />
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      <div className="px-3 py-2 border-t border-gray-100 flex flex-col gap-1.5">
        <div className="text-[9px] font-semibold text-gray-400 uppercase tracking-widest">Suggested</div>
        <div className="flex flex-col gap-1">
          {SUGGESTIONS.slice(0, 3).map((s, i) => (
            <button
              key={i}
              onClick={() => { setInput(s); inputRef.current?.focus() }}
              className="text-left text-[11px] px-2.5 py-1.5 rounded-md border border-gray-200 text-gray-500 hover:border-brand-400 hover:text-brand-600 hover:bg-brand-50 transition-all"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="flex gap-2 px-3 py-2.5 border-t border-gray-200 items-end flex-shrink-0">
        <textarea
          ref={inputRef}
          value={input}
          onChange={e => {
            setInput(e.target.value)
            e.target.style.height = 'auto'
            e.target.style.height = Math.min(e.target.scrollHeight, 80) + 'px'
          }}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
          placeholder="Ask about member risk..."
          className="flex-1 bg-gray-50 border border-gray-200 rounded-lg text-[12px] px-2.5 py-2 outline-none resize-none min-h-[34px] max-h-20 text-gray-800 placeholder:text-gray-400 focus:border-brand-400 transition-colors leading-relaxed"
          rows={1}
        />
        <button
          onClick={send}
          disabled={!input.trim() || loading}
          className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center text-white flex-shrink-0 hover:bg-brand-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-95"
        >
          <Send size={13} />
        </button>
      </div>

    </div>
  )
}