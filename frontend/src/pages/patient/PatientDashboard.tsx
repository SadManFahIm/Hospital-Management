import { motion } from 'framer-motion'
import { CalendarDays, Stethoscope, Activity, Clock } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'

export default function PatientDashboard() {
  const { user } = useAuthStore()
  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="page-title">Hello, {user?.first_name} 👋</h1>
        <p className="page-subtitle">Manage your health appointments and records.</p>
      </motion.div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: 'Total Appointments', value: '12', icon: <CalendarDays size={20} className="text-blue-600" />, bg: 'bg-blue-50' },
          { label: 'Upcoming', value: '2', icon: <Clock size={20} className="text-amber-600" />, bg: 'bg-amber-50' },
          { label: 'Completed', value: '10', icon: <Activity size={20} className="text-emerald-600" />, bg: 'bg-emerald-50' },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} className="stat-card">
            <div className={`stat-icon ${s.bg}`}>{s.icon}</div>
            <div><p className="text-xs text-surface-500">{s.label}</p><p className="text-2xl font-display font-700 text-surface-900">{s.value}</p></div>
          </motion.div>
        ))}
      </div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="card p-6">
        <h3 className="section-title mb-3">Your Next Appointment</h3>
        <div className="flex items-center gap-4 p-4 bg-primary-50 rounded-xl border border-primary-100">
          <div className="w-12 h-12 bg-primary-600 rounded-xl flex items-center justify-center">
            <Stethoscope size={22} className="text-white" />
          </div>
          <div>
            <p className="font-semibold text-surface-900">Dr. Sarah Johnson</p>
            <p className="text-sm text-surface-500">Cardiologist · Feb 18, 2026 at 10:00 AM</p>
          </div>
          <span className="ml-auto badge badge-success">Confirmed</span>
        </div>
      </motion.div>
    </div>
  )
}
