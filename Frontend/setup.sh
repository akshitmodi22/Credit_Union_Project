#!/bin/bash
# Run this from your Frontend folder
# cd "/Users/akshitmodi/Downloads/CU code engine/Frontend"
# bash setup.sh

echo "Creating missing files..."

# ── vite.config.js ─────────────────────────────────────────────
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
EOF

# ── tailwind.config.js ─────────────────────────────────────────
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#EBF2FB',
          100: '#C5DAF5',
          200: '#9FC2EE',
          400: '#5A9AE0',
          600: '#387ED1',
          700: '#2B6AB8',
          800: '#1A5FA8',
          900: '#0D3D70',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      }
    }
  },
  plugins: []
}
EOF

# ── postcss.config.js ──────────────────────────────────────────
cat > postcss.config.js << 'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# ── src/index.css ──────────────────────────────────────────────
cat > src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 text-gray-900 antialiased;
    font-family: 'Inter', system-ui, sans-serif;
  }
  * { box-sizing: border-box; }
}

@layer components {
  .btn {
    @apply inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-150 cursor-pointer border;
  }
  .btn-primary {
    @apply bg-brand-600 text-white border-brand-600 hover:bg-brand-700 active:scale-95;
  }
  .btn-secondary {
    @apply bg-white text-gray-700 border-gray-200 hover:bg-gray-50 active:scale-95;
  }
  .btn-danger {
    @apply bg-white text-red-600 border-red-200 hover:bg-red-50 active:scale-95;
  }
  .btn-ghost {
    @apply bg-transparent text-gray-600 border-transparent hover:bg-gray-100 active:scale-95;
  }
  .card {
    @apply bg-white border border-gray-200 rounded-xl overflow-hidden;
  }
  .card-header {
    @apply flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200;
  }
  .card-title {
    @apply text-sm font-semibold text-gray-800 flex items-center gap-2;
  }
  .input {
    @apply w-full h-8 px-2.5 bg-gray-50 border border-gray-200 rounded-md text-sm text-gray-900 outline-none focus:border-brand-600 focus:ring-1 focus:ring-brand-100 transition-all;
  }
  .select {
    @apply w-full h-8 px-2.5 bg-gray-50 border border-gray-200 rounded-md text-sm text-gray-900 outline-none focus:border-brand-600 transition-all cursor-pointer;
  }
  .badge-high {
    @apply inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-red-50 text-red-700;
  }
  .badge-medium {
    @apply inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-700;
  }
  .badge-low {
    @apply inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-green-50 text-green-700;
  }
  .sidebar-btn {
    @apply w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-all duration-150 border border-transparent text-left cursor-pointer bg-transparent;
  }
  .sidebar-btn.active {
    @apply bg-brand-50 text-brand-700 border-brand-100;
  }
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 2px; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp 0.2s ease; }

@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 0.6s linear infinite; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-4px); opacity: 1; }
}
EOF

# ── src/main.jsx ───────────────────────────────────────────────
cat > src/main.jsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30000 }
  }
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
)
EOF

# ── src/api/index.js ───────────────────────────────────────────
cat > src/api/index.js << 'EOF'
const BASE = '/api'

async function request(url, options = {}) {
  const res = await fetch(`${BASE}${url}`, options)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export const getHealth = () => request('/health')
export const getModelHealth = () => request('/model-health')

export const smartQuery = ({ model, tier, branch, county, age_band, income_band, life_stage, min_prob, top_n }) => {
  const qp = new URLSearchParams()
  qp.set('model', model)
  if (top_n)       qp.set('top_n', top_n)
  if (tier)        qp.set('tier', tier)
  if (branch)      qp.set('branch', branch)
  if (county)      qp.set('county', county)
  if (age_band)    qp.set('age_band', age_band)
  if (income_band) qp.set('income_band', income_band)
  if (life_stage)  qp.set('life_stage', life_stage)
  if (min_prob)    qp.set('min_prob', min_prob)
  return request(`/smart-query?${qp}`, { method: 'POST' })
}

export const getAvailableFilters = (model) => request(`/available-filters?model=${model}`)
export const runPredictions = (model) => request(`/run-predictions?model=${model}`, { method: 'POST' })
export const runRetrain = (model) => request(`/retrain?model=${model}`, { method: 'POST' })

export const getUnifiedReport = (branch) => {
  const qp = new URLSearchParams()
  if (branch) qp.set('branch', branch)
  return request(`/unified-report?${qp}`, { method: 'POST' })
}

export const generateChart = ({ model, group_by = 'branch_assignment', tier }) => {
  const qp = new URLSearchParams({ model, group_by })
  if (tier) qp.set('tier', tier)
  return request(`/generate-chart?${qp}`, { method: 'POST' })
}
EOF

# ── src/store/index.js ─────────────────────────────────────────
cat > src/store/index.js << 'EOF'
import { create } from 'zustand'

export const useStore = create((set) => ({
  model: 'attrition',
  setModel: (model) => set({ model }),

  filters: {
    tier: '', branch: '', county: '', age_band: '',
    income_band: '', life_stage: '', min_prob: '', top_n: 20,
  },
  setFilter: (key, value) =>
    set((state) => ({ filters: { ...state.filters, [key]: value } })),
  resetFilters: () =>
    set({ filters: { tier:'', branch:'', county:'', age_band:'', income_band:'', life_stage:'', min_prob:'', top_n:20 } }),

  stats: null,
  setStats: (stats) => set({ stats }),

  serverOnline: false,
  setServerOnline: (v) => set({ serverOnline: v }),

  toasts: [],
  addToast: (msg, type = 'info') =>
    set((state) => ({ toasts: [...state.toasts, { id: Date.now(), msg, type }] })),
  removeToast: (id) =>
    set((state) => ({ toasts: state.toasts.filter(t => t.id !== id) })),
}))
EOF

# ── src/hooks/useNLP.js ────────────────────────────────────────
cat > src/hooks/useNLP.js << 'EOF'
export function parseNL(text, currentModel) {
  const l = text.toLowerCase()
  const result = { intent: 'smart_query', model: currentModel, params: {} }

  if (l.includes('attrition') || l.includes('churn')) result.model = 'attrition'
  else if (l.includes('loan') || l.includes('offer')) result.model = 'loan'
  else if (l.includes('propensity') || l.includes('deposit')) result.model = 'propensity'

  if (l.includes('retrain') || l.includes('train model')) result.intent = 'retrain'
  else if (l.includes('predict') || l.includes('batch')) result.intent = 'predictions'
  else if (l.includes('health') || l.includes('auc')) result.intent = 'health'
  else if (l.includes('unified') || l.includes('all model')) result.intent = 'unified'
  else if (l.includes('chart') || l.includes('graph')) result.intent = 'chart'
  else if (l.includes('filter') || l.includes('available')) result.intent = 'filters'

  if (l.includes('high risk') || l.includes('at risk') || l.includes('high propensity')) result.params.tier = 'High'
  else if (l.includes('medium')) result.params.tier = 'Medium'
  else if (l.includes('low risk')) result.params.tier = 'Low'

  const branches = ['hartford','cromwell','glastonbury','east hartford','north haven','new haven','newington','enfield']
  for (const b of branches) {
    if (l.includes(b)) {
      result.params.branch = b.split(' ').map(w => w[0].toUpperCase() + w.slice(1)).join(' ')
      break
    }
  }

  const nm = text.match(/top\s+(\d+)/i) || text.match(/(\d+)\s+(?:customer|member)/i)
  if (nm) result.params.top_n = parseInt(nm[1])

  const pm = text.match(/above\s+([\d.]+)\s*%/i) || text.match(/more than\s+([\d.]+)\s*%/i)
  if (pm) result.params.min_prob = parseFloat(pm[1]) > 1 ? parseFloat(pm[1]) / 100 : parseFloat(pm[1])

  return result
}
EOF

echo "All files created!"
echo ""
echo "Now run:"
echo "  npm install"
echo "  npm run dev"
