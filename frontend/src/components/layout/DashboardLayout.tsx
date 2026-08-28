import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, Users, UserRound, CalendarDays,
  Stethoscope, LogOut, Menu, X, Heart, Bell, ChevronDown,
  ClipboardList, Activity
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authAPI } from '@/services/api'
import toast from 'react-hot-toast'
import clsx from 'clsx'

interface NavItem {
  label: string
  to: string
  icon: React.ReactNode
}

const adminNav: NavItem[] = [
  { label: 'Dashboard', to: '/admin/dashboard', icon: <LayoutDashboard size={18} /> },
  { label: 'Doctors', to: '/admin/doctors', icon: <Stethoscope size={18} /> },
  { label: 'Patients', to: '/admin/patients', icon: <UserRound size={18} /> },
  { label: 'Appointments', to: '/admin/appointments', icon: <CalendarDays size={18} /> },
]

const doctorNav: NavItem[] = [
  { label: 'Dashboard', to: '/doctor/dashboard', icon: <LayoutDashboard size={18} /> },
  { label: 'Appointments', to: '/doctor/appointments', icon: <CalendarDays size={18} /> },
  { label: 'My Patients', to: '/doctor/patients', icon: <UserRound size={18} /> },
]

const patientNav: NavItem[] = [
  { label: 'Dashboard', to: '/patient/dashboard', icon: <LayoutDashboard size={18} /> },
  { label: 'Appointments', to: '/patient/appointments', icon: <CalendarDays size={18} /> },
  { label: 'Find Doctors', to: '/patient/doctors', icon: <Stethoscope size={18} /> },
]

const navByRole = { admin: adminNav, doctor: doctorNav, patient: patientNav }

const roleBadgeConfig = {
  admin: { label: 'Administrator', color: 'bg-violet-100 text-violet-700' },
  doctor: { label: 'Doctor', color: 'bg-blue-100 text-blue-700' },
  patient: { label: 'Patient', color: 'bg-emerald-100 text-emerald-700' },
}

export default function DashboardLayout({ role }: { role: 'admin' | 'doctor' | 'patient' }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const navItems = navByRole[role]
  const roleConfig = roleBadgeConfig[role]

  const handleLogout = async () => {
    // Best effort: revoke the refresh token server-side before clearing local state.
    const refreshToken = useAuthStore.getState().refreshToken
    try {
      if (refreshToken) {
        await authAPI.logout(refreshToken)
      }
    } catch {}
    logout()
    navigate('/login')
    toast.success('Logged out successfully')
  }

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-surface-100">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-primary-600 rounded-xl flex items-center justify-center shadow-glow">
            <Heart size={18} className="text-white" />
          </div>
          <AnimatePresence>
            {sidebarOpen && (
              <motion.div
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
                transition={{ duration: 0.15 }}
              >
                <span className="font-display font-700 text-surface-900 text-lg">MedCore</span>
                <span className="font-display font-400 text-primary-600 text-lg"> HMS</span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Nav Items */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <AnimatePresence>
          {sidebarOpen && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-xs font-semibold text-surface-400 uppercase tracking-wider px-3 mb-2"
            >
              Navigation
            </motion.p>
          )}
        </AnimatePresence>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              clsx(
                'sidebar-link',
                isActive && 'active',
                !sidebarOpen && 'justify-center px-2'
              )
            }
            title={!sidebarOpen ? item.label : undefined}
          >
            <span className="flex-shrink-0">{item.icon}</span>
            <AnimatePresence>
              {sidebarOpen && (
                <motion.span
                  initial={{ opacity: 0, x: -4 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  className="truncate"
                >
                  {item.label}
                </motion.span>
              )}
            </AnimatePresence>
          </NavLink>
        ))}
      </nav>

      {/* User Profile */}
      <div className="p-3 border-t border-surface-100">
        <div
          className={clsx(
            'flex items-center gap-3 rounded-xl p-2.5 hover:bg-surface-100 cursor-pointer transition-colors',
            !sidebarOpen && 'justify-center'
          )}
        >
          <div className="w-8 h-8 bg-primary-600 rounded-xl flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-bold">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </span>
          </div>
          <AnimatePresence>
            {sidebarOpen && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 min-w-0"
              >
                <p className="text-sm font-medium text-surface-900 truncate">
                  {user?.first_name} {user?.last_name}
                </p>
                <span className={clsx('text-xs px-1.5 py-0.5 rounded-md font-medium', roleConfig.color)}>
                  {roleConfig.label}
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        <button
          onClick={handleLogout}
          className={clsx(
            'w-full flex items-center gap-3 rounded-xl p-2.5 mt-1',
            'text-red-500 hover:bg-red-50 transition-colors text-sm font-medium',
            !sidebarOpen && 'justify-center'
          )}
        >
          <LogOut size={16} />
          <AnimatePresence>
            {sidebarOpen && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                Logout
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen bg-surface-50 overflow-hidden">
      {/* Desktop Sidebar */}
      <motion.aside
        animate={{ width: sidebarOpen ? 260 : 72 }}
        transition={{ duration: 0.2, ease: 'easeInOut' }}
        className="hidden lg:flex flex-col bg-white border-r border-surface-100 shadow-sm flex-shrink-0 z-30"
      >
        <SidebarContent />
      </motion.aside>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {mobileSidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileSidebarOpen(false)}
              className="fixed inset-0 bg-black/40 z-40 lg:hidden"
            />
            <motion.aside
              initial={{ x: -260 }}
              animate={{ x: 0 }}
              exit={{ x: -260 }}
              transition={{ duration: 0.2 }}
              className="fixed left-0 top-0 h-full w-[260px] bg-white border-r border-surface-100 shadow-xl z-50 lg:hidden"
            >
              <SidebarContent />
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-white border-b border-surface-100 flex items-center justify-between px-4 lg:px-6 flex-shrink-0">
          <div className="flex items-center gap-3">
            {/* Mobile menu button */}
            <button
              onClick={() => setMobileSidebarOpen(true)}
              className="lg:hidden btn-ghost text-surface-600"
            >
              <Menu size={20} />
            </button>
            {/* Desktop collapse button */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="hidden lg:flex btn-ghost text-surface-500"
            >
              <Menu size={18} />
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button className="btn-ghost relative">
              <Bell size={18} className="text-surface-500" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary-500 rounded-full"></span>
            </button>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl hover:bg-surface-100 cursor-pointer">
              <div className="w-7 h-7 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-xs font-bold">
                  {user?.first_name?.[0]}{user?.last_name?.[0]}
                </span>
              </div>
              <span className="hidden sm:block text-sm font-medium text-surface-700">
                {user?.first_name} {user?.last_name}
              </span>
              <ChevronDown size={14} className="text-surface-400" />
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-4 lg:p-6 max-w-7xl mx-auto animate-fade-in">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
