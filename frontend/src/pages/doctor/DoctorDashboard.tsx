import { motion } from 'framer-motion'
import { Users, CalendarDays, Clock, TrendingUp } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'

export default function DoctorDashboard() {
  const { user } = useAuthStore()
  const stats = [
    { label: 'My Patients', value: '28', icon: <Users size={20} className="text-blue-600" />, bg: 'bg-blue-50', trend: '+3 this week' },
    { label: "Today's Appointments", value: '6', icon: <CalendarDays size={20} className="text-emerald-600" />, bg: 'bg-emerald-50', trend: '2 pending' },
    { label: 'Pending Approvals', value: '4', icon: <Clock size={20} className="text-amber-600" />, bg: 'bg-amber-50', trend: 'Needs action' },
    { label: 'Completed This Month', value: '87', icon: <TrendingUp size={20} className="text-violet-600" />, bg: 'bg-violet-50', trend: '+12% vs last month' },
  ]

  const upcomingAppts = [
    { time: '09:00 AM', patient: 'John Doe', type: 'Follow-up', status: 'confirmed' },
    { time: '10:30 AM', patient: 'Maria Garcia', type: 'New Patient', status: 'confirmed' },
    { time: '11:00 AM', patient: 'Ahmed Khan', type: 'Routine', status: 'pending' },
    { time: '02:00 PM', patient: 'Fatima Begum', type: 'Consultation', status: 'confirmed' },
    { time: '03:30 PM', patient: 'Robert Wilson', type: 'Follow-up', status: 'confirmed' },
  ]

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="page-title">Good morning, Dr. {user?.last_name} 👋</h1>
        <p className="page-subtitle">You have 6 appointments scheduled for today.</p>
      </motion.div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div key={stat.label} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }} className="stat-card">
            <div className={`stat-icon ${stat.bg}`}>{stat.icon}</div>
            <div>
              <p className="text-xs text-surface-500">{stat.label}</p>
              <p className="text-2xl font-display font-700 text-surface-900">{stat.value}</p>
              <p className="text-xs text-surface-400 mt-0.5">{stat.trend}</p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="card p-5">
          <h3 className="section-title mb-4">Today's Schedule</h3>
          <div className="space-y-3">
            {upcomingAppts.map((appt, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-xl hover:bg-surface-50 transition-colors">
                <div className="w-16 text-center flex-shrink-0">
                  <p className="text-xs font-semibold text-primary-600">{appt.time}</p>
                </div>
                <div className="w-px h-8 bg-surface-200 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-surface-900">{appt.patient}</p>
                  <p className="text-xs text-surface-400">{appt.type}</p>
                </div>
                <span className={appt.status === 'confirmed' ? 'badge badge-success' : 'badge badge-warning'}>
                  {appt.status}
                </span>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }} className="card p-5">
          <h3 className="section-title mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'View All Appointments', icon: <CalendarDays size={18} />, color: 'bg-blue-50 text-blue-700 hover:bg-blue-100' },
              { label: 'My Patients', icon: <Users size={18} />, color: 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100' },
              { label: 'Pending Reviews', icon: <Clock size={18} />, color: 'bg-amber-50 text-amber-700 hover:bg-amber-100' },
              { label: 'Monthly Report', icon: <TrendingUp size={18} />, color: 'bg-violet-50 text-violet-700 hover:bg-violet-100' },
            ].map((action) => (
              <button key={action.label} className={`flex flex-col items-center gap-2 p-4 rounded-xl transition-colors ${action.color}`}>
                {action.icon}
                <span className="text-xs font-medium text-center">{action.label}</span>
              </button>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
