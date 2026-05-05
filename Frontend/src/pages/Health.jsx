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
