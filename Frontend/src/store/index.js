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
