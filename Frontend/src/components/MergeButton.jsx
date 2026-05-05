// ═══════════════════════════════════════════════════════════════
// components/MergeButton.jsx
// Reusable merge button used in Sidebar and Members page
// ═══════════════════════════════════════════════════════════════

import { useState, useEffect } from 'react'
import { GitMerge, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import { mergePredictions, getMergeStatus } from '../api'
import { useStore } from '../store'
import { Spinner } from './UI'

export default function MergeButton({ compact = false }) {
  const addToast = useStore(s => s.addToast)
  const [loading,  setLoading]  = useState(false)
  const [status,   setStatus]   = useState(null)  // merge status from backend
  const [merging,  setMerging]  = useState(false)

  // Load merge status on mount
  useEffect(() => {
    getMergeStatus()
      .then(s => setStatus(s))
      .catch(() => setStatus(null))
  }, [])

  async function handleMerge() {
    if (!window.confirm(
      'Merge latest predictions from all 3 models into master CSV?\n\n' +
      'Make sure all 3 prediction jobs have run successfully first.'
    )) return

    setLoading(true)
    setMerging(true)
    try {
      const result = await mergePredictions()
      setStatus({
        status        : 'exists',
        merged_at     : result.merged_at,
        total_members : result.total_members,
        models        : result.models_included,
      })
      addToast(`Master CSV created! ${result.total_members?.toLocaleString()} members merged`, 'success')
    } catch (e) {
      addToast(`Merge failed: ${e.message}`, 'error')
    }
    setLoading(false)
    setMerging(false)
  }

  // Compact version for sidebar
  if (compact) {
    return (
      <div className="flex flex-col gap-1.5">
        <button
          onClick={handleMerge}
          disabled={loading}
          className="sidebar-btn text-purple-600 hover:bg-purple-50 hover:text-purple-700"
        >
          {loading
            ? <><Spinner size={11} /> Merging...</>
            : <><GitMerge size={13} /> Merge Predictions</>
          }
        </button>
        {status?.status === 'exists' && (
          <div className="flex items-center gap-1 px-3 text-[10px] text-green-600">
            <CheckCircle size={9} />
            Merged · {status.merged_at}
          </div>
        )}
        {status?.status === 'not_merged' && (
          <div className="flex items-center gap-1 px-3 text-[10px] text-amber-500">
            <AlertCircle size={9} />
            Not merged yet
          </div>
        )}
      </div>
    )
  }

  // Full version for Members page
  return (
    <div className="flex items-center gap-3">
      <button
        onClick={handleMerge}
        disabled={loading}
        className="btn btn-secondary text-xs gap-1.5 border-purple-200 text-purple-700 hover:bg-purple-50"
      >
        {loading
          ? <><Spinner size={11} /> Merging all models...</>
          : <><GitMerge size={12} /> Merge Predictions</>
        }
      </button>

      {status?.status === 'exists' && (
        <div className="flex items-center gap-1.5 text-[11px] text-green-600">
          <CheckCircle size={12} />
          <span>
            Master CSV ready · {status.merged_at} · {status.total_members?.toLocaleString()} members
          </span>
        </div>
      )}

      {status?.status === 'not_merged' && (
        <div className="flex items-center gap-1.5 text-[11px] text-amber-500">
          <AlertCircle size={12} />
          <span>No master CSV yet — run all 3 predictions first then merge</span>
        </div>
      )}
    </div>
  )
}
