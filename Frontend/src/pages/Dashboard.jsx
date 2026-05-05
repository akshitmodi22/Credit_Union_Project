import { useState, useEffect } from 'react'
import { useStore } from '../store'
import {
  smartQuery, runPredictions, runRetrain,
  getModelHealth, getUnifiedReport, generateChart, getAvailableFilters
} from '../api'
import Sidebar from '../components/Sidebar'
import StatsBar from '../components/StatsBar'
import ChatPanel from '../components/ChatPanel'
import { EmptyState, LoadingCard } from '../components/UI'
import {
  SmartQueryCard, HealthCard, JobCard,
  ChartCard, UnifiedCard, FiltersCard
} from '../components/ResultCards'
import ModelInfoModal from '../components/ModelInfoModal'

export default function Dashboard() {
  const model    = useStore(s => s.model)
  const filters  = useStore(s => s.filters)
  const setStats = useStore(s => s.setStats)
  const addToast = useStore(s => s.addToast)

  const [results, setResults]   = useState([])
  const [loading, setLoading]   = useState(false)
  const [loadMsg, setLoadMsg]   = useState('')
  const [infoModel, setInfoModel] = useState(null)

  // Load Orchestrate floating widget
  useEffect(() => {
    window.wxOConfiguration = {
      orchestrationID: "baf3554ebf3c4225ac4c4e9efb79516b_93bec19d-601a-4d86-9aae-ac29998dfae6",
      hostURL: "https://us-south.watson-orchestrate.cloud.ibm.com",
      rootElementID: "wxo-float",
      deploymentPlatform: "ibmcloud",
      crn: "crn:v1:bluemix:public:watsonx-orchestrate:us-south:a/baf3554ebf3c4225ac4c4e9efb79516b:93bec19d-601a-4d86-9aae-ac29998dfae6::",
      chatOptions: {
        agentId: "231bab88-cf07-46c4-8c2d-441398a3ac5b",
      }
    }
    setTimeout(function () {
      const script = document.createElement('script')
      script.src = `${window.wxOConfiguration.hostURL}/wxochat/wxoLoader.js?embed=true`
      script.addEventListener('load', function () {
        if (window.wxoLoader) wxoLoader.init()
      })
      document.head.appendChild(script)
    }, 0)
  }, [])

  function addResult(result) {
    setResults(prev => [result, ...prev])
  }

  function handleChatResult({ type, data, model: m, title }) {
    if (type === 'smart_query' && data.summary) {
      setStats(data.summary)
    }
    addResult({ type, data, model: m || model, title })
  }

  async function handleAction(action) {
    if (action === 'retrain') {
      if (!window.confirm(`Retrain ${model} model? This may take 10+ minutes.`)) return
    }

    const msgs = {
      smart_query: 'Querying members...',
      filters:     'Loading filter options...',
      unified:     'Generating unified report...',
      chart:       'Generating branch chart...',
      predictions: 'Triggering batch predictions...',
      retrain:     'Triggering model retraining...',
      health:      'Checking model health...',
    }

    setLoading(true)
    setLoadMsg(msgs[action] || 'Loading...')

    try {
      let data, type

      if (action === 'smart_query') {
        data = await smartQuery({ model, ...filters })
        type = 'smart_query'
        if (data.summary) setStats(data.summary)
      }
      else if (action === 'filters') {
        data = await getAvailableFilters(model)
        type = 'filters'
      }
      else if (action === 'unified') {
        data = await getUnifiedReport(filters.branch)
        type = 'unified'
      }
      else if (action === 'chart') {
        data = await generateChart({ model, tier: filters.tier || 'High' })
        type = 'chart'
      }
      else if (action === 'predictions') {
        data = await runPredictions(model)
        type = 'job'
        addToast(`Predictions triggered for ${model}`, 'success')
      }
      else if (action === 'retrain') {
        data = await runRetrain(model)
        type = 'job'
        addToast(`Retrain triggered for ${model}`, 'success')
      }
      else if (action === 'health') {
        data = await getModelHealth()
        type = 'health'
      }

      addResult({ type, data, model, title: action === 'predictions' ? 'Batch Predictions' : 'Model Retraining' })

    } catch (e) {
      addToast(`Error: ${e.message}`, 'error')
    }

    setLoading(false)
  }

  return (
    <div className="flex flex-1 overflow-hidden">

      <Sidebar onAction={handleAction} onModelInfo={setInfoModel} />

      <div className="flex flex-col flex-1 overflow-hidden min-w-0">
        <StatsBar />

        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
          {loading && <LoadingCard message={loadMsg} />}

          {results.length === 0 && !loading && <EmptyState />}

          {results.map((r, i) => {
            if (r.type === 'smart_query') return <SmartQueryCard key={i} data={r.data} model={r.model} />
            if (r.type === 'health')      return <HealthCard key={i} data={r.data} />
            if (r.type === 'job')         return <JobCard key={i} data={r.data} title={r.title} />
            if (r.type === 'chart')       return <ChartCard key={i} data={r.data} />
            if (r.type === 'unified')     return <UnifiedCard key={i} data={r.data} />
            if (r.type === 'filters')     return <FiltersCard key={i} data={r.data} />
            return null
          })}
        </div>
      </div>

      <ChatPanel onResult={handleChatResult} />

      <div id="wxo-float" />

      {infoModel && <ModelInfoModal model={infoModel} onClose={() => setInfoModel(null)} />}

    </div>
  )
}