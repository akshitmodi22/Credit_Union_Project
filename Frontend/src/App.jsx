import { Routes, Route } from 'react-router-dom'
import Topbar from './components/Topbar'
import { ToastContainer } from './components/UI'
import Dashboard from './pages/Dashboard'
import Members from './pages/Members'
import Jobs from './pages/Jobs'
import Health from './pages/Health'

export default function App() {
  return (
    <div className="flex flex-col h-screen overflow-hidden bg-gray-50">
      <Topbar />
      <div className="flex flex-1 overflow-hidden">
        <Routes>
          <Route path="/"        element={<Dashboard />} />
          <Route path="/members" element={<Members />} />
          <Route path="/jobs"    element={<Jobs />} />
          <Route path="/health"  element={<Health />} />
        </Routes>
      </div>
      <ToastContainer />
    </div>
  )
}