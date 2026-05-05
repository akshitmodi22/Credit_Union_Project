import { NavLink } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { LayoutDashboard, Users, Briefcase, Activity } from 'lucide-react'
import { clsx } from 'clsx'
import { getHealth } from '../api'
import { useStore } from '../store'

const NAV = [
  { to: '/',        label: 'Dashboard', icon: LayoutDashboard },
  { to: '/members', label: 'Members',   icon: Users },
  { to: '/jobs',    label: 'Jobs',      icon: Briefcase },
  { to: '/health',  label: 'Health',    icon: Activity },
]

export default function Topbar() {
  const setServerOnline = useStore(s => s.setServerOnline)
  useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const d = await getHealth()
      setServerOnline(d.status === 'ok')
      return d
    },
    refetchInterval: 30000,
  })
  const serverOnline = useStore(s => s.serverOnline)

  return (
    <header className="bg-white border-b border-gray-200 flex items-center px-5 gap-6 flex-shrink-0 z-10" style={{height:52}}>
      <div className="flex items-center gap-2 font-semibold text-sm text-gray-900 select-none">
        <div className="w-6 h-6 bg-brand-600 rounded-md flex items-center justify-center text-white text-[10px] font-bold">CU</div>
        Credit Union Intelligence
      </div>
      <nav className="flex items-center gap-0.5 flex-1">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === '/'}
            className={({ isActive }) => clsx(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all',
              isActive ? 'bg-brand-50 text-brand-700' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-100'
            )}
          >
            <Icon size={13} />{label}
          </NavLink>
        ))}
      </nav>
      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gray-50 border border-gray-200 text-[11px] font-mono text-gray-500">
        <div className={clsx('w-1.5 h-1.5 rounded-full', serverOnline ? 'bg-green-500' : 'bg-red-500')} />
        {serverOnline ? 'Online · 8080' : 'Offline'}
      </div>
    </header>
  )
}