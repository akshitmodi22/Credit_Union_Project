import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Play, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react'
import { runPredictions, runRetrain, getModelHealth } from '../api'
import { useStore } from '../store'
import { Spinner } from '../components/UI'

const MODELS = ['attrition', 'loan', 'propensity']

export default function Jobs() {
  const addToast = useStore(s => s.addToast)
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState({})

  const { data: healthData } = useQuery({
    queryKey: ['model-health-jobs'],
    queryFn: getModelHealth,
    staleTime: 30000,
  })

  const models = healthData?.models || {}

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
        <div className="max-w-4xl mx-auto flex flex-col gap-6">

          {/* Model Status Cards */}
          <div>
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Model Status</div>
            <div className="grid grid-cols-3 gap-3">
              {MODELS.map(model => {
                const info = models[model] || {}
                const isHealthy = info.status === 'healthy'
                return (
                  <div key={`status-${model}`} className="bg-white border border-gray-200 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="text-sm font-semibold capitalize text-gray-800">{model}</div>
                      {info.status && (
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium ${
                          isHealthy ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-amber-500'}`} />
                          {info.status}
                        </span>
                      )}
                    </div>
                    <div className="flex flex-col gap-1.5 text-[11px]">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Version</span>
                        <span className="font-mono text-gray-700 font-medium">v{info.version || '—'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">AUC</span>
                        <span className={`font-mono font-medium ${isHealthy ? 'text-green-600' : 'text-amber-600'}`}>{info.auc || '—'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Last Trained</span>
                        <span className="font-mono text-blue-600">{info.trained_on || '—'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Last Predicted</span>
                        <span className="font-mono text-purple-600">{info.predicted_on || info.trained_on || '—'}</span>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Trigger Jobs */}
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

          {/* Run History */}
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