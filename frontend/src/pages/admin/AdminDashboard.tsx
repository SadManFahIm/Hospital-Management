import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  Users, Stethoscope, CalendarDays, UserRound,
  TrendingUp, Activity, Clock, DollarSign,
  CheckCircle, AlertCircle
} from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts'
import { dashboardAPI } from '@/services/api'
import { useAuthStore } from '@/store/authStore'
import clsx from 'clsx'

const appointmentTrendData = [
  { month: 'Aug', appointments: 65, patients: 42 },
  { month: 'Sep', appointments: 82, patients: 57 },
  { month: 'Oct', appointments: 91, patients: 63 },
  { month: 'Nov', appointments: 78, patients: 51 },
  { month: 'Dec', appointments: 105, patients: 74 },
  { month: 'Jan', appointments: 119, patients: 88 },
  { month: 'Feb', appointments: 134, patients: 97 },
]

const departmentData = [
  { name: 'Cardiology', value: 28, color: '#3893f6' },
  { name: 'Neurology', value: 22, color: '#8b5cf6' },
  { name: 'Orthopedic', value: 18, color: '#10b981' },
  { name: 'Pediatrics', value: 15, color: '#f59e0b' },
  { name: 'Others', value: 17, color: '#94a3b8' },
]

const weeklyData = [
  { day: 'Mon', count: 24 },
  { day: 'Tue', count: 31 },
  { day: 'Wed', count: 28 },
  { day: 'Thu', count: 36 },
  { day: 'Fri', count: 42 },
  { day: 'Sat', count: 18 },
  { day: 'Sun', count: 12 },
]

const recentActivities = [
  { action: 'New doctor registered', detail: 'Dr. Sarah Johnson - Cardiology', time: '5m ago', type: 'doctor' },
  { action: 'Appointment completed', detail: 'Patient: John Doe with Dr. Smith', time: '12m ago', type: 'appointment' },
  { action: 'Patient admitted', detail: 'Emily Chen - Room 204', time: '28m ago', type: 'patient' },
  { action: 'Discharge processed', detail: 'Robert Wilson - Invoice #INV-2847', time: '1h ago', type: 'discharge' },
  { action: 'New appointment booked', detail: 'Maria Garcia - Dr. Patel', time: '1.5h ago', type: 'appointment' },
]

const activityTypeStyle = {
  doctor: 'bg-blue-50 text-blue-600 border-blue-200',
  appointment: 'bg-emerald-50 text-emerald-600 border-emerald-200',
  patient: 'bg-amber-50 text-amber-600 border-amber-200',
  discharge: 'bg-violet-50 text-violet-600 border-violet-200',
}

interface StatCardProps {
  label: string
  value: string | number
  subtitle?: string
  icon: React.ReactNode
  iconBg: string
  trend?: { value: number; positive: boolean }
  delay?: number
}

function StatCard({ label, value, subtitle, icon, iconBg, trend, delay = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.3 }}
      className="stat-card"
    >
      <div className={clsx('stat-icon', iconBg)}>{icon}</div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-surface-500 font-medium truncate">{label}</p>
        <p className="text-2xl font-display font-700 text-surface-900 mt-0.5">{value}</p>
        {subtitle && <p className="text-xs text-surface-400 mt-0.5">{subtitle}</p>}
        {trend && (
          <div className={clsx('flex items-center gap-1 mt-1 text-xs font-medium',
            trend.positive ? 'text-emerald-600' : 'text-red-500')}>
            <TrendingUp size={12} className={trend.positive ? '' : 'rotate-180'} />
            <span>{trend.value}% vs last month</span>
          </div>
        )}
      </div>
    </motion.div>
  )
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface-900 text-white px-3 py-2 rounded-xl text-xs shadow-xl border border-surface-700">
      <p className="font-medium mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }}>{p.name}: {p.value}</p>
      ))}
    </div>
  )
}

export default function AdminDashboard() {
  const { user } = useAuthStore()
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      try {
        const { data } = await dashboardAPI.adminStats()
        return data
      } catch {
        // Return mock data if API not running
        return {
          total_doctors: 47,
          total_patients: 312,
          total_appointments: 1284,
          pending_appointments: 23,
          admitted_patients: 18,
          todays_appointments: 34,
          revenue_this_month: 284500,
          approved_doctors: 42,
        }
      }
    },
  })

  const statCards = [
    {
      label: 'Total Doctors',
      value: stats?.total_doctors ?? '—',
      subtitle: `${stats?.approved_doctors ?? 0} approved`,
      icon: <Stethoscope size={20} className="text-blue-600" />,
      iconBg: 'bg-blue-50',
      trend: { value: 12, positive: true },
    },
    {
      label: 'Total Patients',
      value: stats?.total_patients ?? '—',
      subtitle: `${stats?.admitted_patients ?? 0} admitted`,
      icon: <UserRound size={20} className="text-emerald-600" />,
      iconBg: 'bg-emerald-50',
      trend: { value: 8, positive: true },
    },
    {
      label: "Today's Appointments",
      value: stats?.todays_appointments ?? '—',
      subtitle: `${stats?.pending_appointments ?? 0} pending`,
      icon: <CalendarDays size={20} className="text-amber-600" />,
      iconBg: 'bg-amber-50',
      trend: { value: 5, positive: true },
    },
    {
      label: 'Monthly Revenue',
      value: stats ? `৳${(stats.revenue_this_month / 1000).toFixed(0)}K` : '—',
      subtitle: 'From discharges',
      icon: <DollarSign size={20} className="text-violet-600" />,
      iconBg: 'bg-violet-50',
      trend: { value: 15, positive: true },
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="page-header"
      >
        <h1 className="page-title">
          Good morning, {user?.first_name} 👋
        </h1>
        <p className="page-subtitle">
          Here's what's happening at your hospital today.
        </p>
      </motion.div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {statCards.map((card, i) => (
          <StatCard key={card.label} {...card} delay={i * 0.06} />
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Area Chart */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card xl:col-span-2 p-5"
        >
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="section-title">Appointment Trends</h3>
              <p className="text-xs text-surface-400 mt-0.5">Last 7 months overview</p>
            </div>
            <span className="badge badge-success">
              <Activity size={10} />
              Live
            </span>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={appointmentTrendData}>
              <defs>
                <linearGradient id="colorAppt" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3893f6" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#3893f6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorPat" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="appointments" stroke="#3893f6" strokeWidth={2} fill="url(#colorAppt)" name="Appointments" />
              <Area type="monotone" dataKey="patients" stroke="#10b981" strokeWidth={2} fill="url(#colorPat)" name="New Patients" />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Pie Chart */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="card p-5"
        >
          <h3 className="section-title mb-1">By Department</h3>
          <p className="text-xs text-surface-400 mb-4">Appointment distribution</p>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie data={departmentData} cx="50%" cy="50%" innerRadius={45} outerRadius={70}
                dataKey="value" paddingAngle={3}>
                {departmentData.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-3 space-y-1.5">
            {departmentData.map((d) => (
              <div key={d.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: d.color }} />
                  <span className="text-xs text-surface-600">{d.name}</span>
                </div>
                <span className="text-xs font-medium text-surface-900">{d.value}%</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Bar Chart */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card p-5"
        >
          <h3 className="section-title mb-1">This Week</h3>
          <p className="text-xs text-surface-400 mb-4">Daily appointment count</p>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={weeklyData} barSize={20}>
              <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" fill="#3893f6" radius={[6, 6, 0, 0]} name="Appointments" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.45 }}
          className="card xl:col-span-2 p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="section-title">Recent Activity</h3>
            <button className="text-xs text-primary-600 font-medium hover:text-primary-700">View all</button>
          </div>
          <div className="space-y-3">
            {recentActivities.map((activity, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + i * 0.05 }}
                className="flex items-start gap-3"
              >
                <span className={clsx(
                  'flex-shrink-0 text-xs px-2 py-0.5 rounded-md border capitalize mt-0.5',
                  activityTypeStyle[activity.type as keyof typeof activityTypeStyle]
                )}>
                  {activity.type}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-surface-800">{activity.action}</p>
                  <p className="text-xs text-surface-400 truncate">{activity.detail}</p>
                </div>
                <span className="text-xs text-surface-400 flex-shrink-0 flex items-center gap-1">
                  <Clock size={10} />
                  {activity.time}
                </span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
