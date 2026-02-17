import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Heart, Mail, Lock, Eye, EyeOff, ArrowRight, Activity } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authAPI } from '@/services/api'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      toast.error('Please fill in all fields')
      return
    }
    setIsLoading(true)
    try {
      const { data } = await authAPI.login(email, password)
      setAuth(data.user, data.access_token, data.refresh_token)
      toast.success(`Welcome back, ${data.user.first_name}!`)

      const role = data.user.role
      if (role === 'admin') navigate('/admin/dashboard')
      else if (role === 'doctor') navigate('/doctor/dashboard')
      else navigate('/patient/dashboard')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  // Demo credentials helper
  const fillDemo = (role: 'admin' | 'doctor' | 'patient') => {
    const creds = {
      admin: { email: 'admin@medcore.com', password: 'Admin@1234' },
      doctor: { email: 'doctor@medcore.com', password: 'Doctor@1234' },
      patient: { email: 'patient@medcore.com', password: 'Patient@1234' },
    }
    setEmail(creds[role].email)
    setPassword(creds[role].password)
  }

  return (
    <div className="min-h-screen bg-surface-950 flex">
      {/* Left panel - decorative */}
      <div className="hidden lg:flex flex-1 flex-col justify-between p-12 relative overflow-hidden">
        {/* Background gradients */}
        <div className="absolute inset-0">
          <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-primary-600/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-violet-600/15 rounded-full blur-3xl translate-x-1/2 translate-y-1/2" />
        </div>

        {/* Grid pattern overlay */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), 
                              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        />

        <div className="relative">
          <div className="flex items-center gap-3 mb-16">
            <div className="w-10 h-10 bg-primary-500 rounded-xl flex items-center justify-center">
              <Heart size={20} className="text-white" />
            </div>
            <span className="font-display font-700 text-white text-xl">MedCore HMS</span>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h1 className="text-5xl font-display font-800 text-white leading-tight mb-6">
              Modern Healthcare
              <span className="text-primary-400 block">Management</span>
            </h1>
            <p className="text-surface-400 text-lg leading-relaxed max-w-md">
              Streamline your hospital operations with our comprehensive management platform.
              Built for modern healthcare teams.
            </p>
          </motion.div>
        </div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="relative grid grid-cols-3 gap-4"
        >
          {[
            { label: 'Patients Managed', value: '10K+' },
            { label: 'Doctors Network', value: '500+' },
            { label: 'Appointments Daily', value: '1,200' },
          ].map((stat) => (
            <div key={stat.label} className="bg-white/5 backdrop-blur rounded-2xl p-4 border border-white/10">
              <p className="text-2xl font-display font-700 text-white">{stat.value}</p>
              <p className="text-surface-500 text-sm mt-0.5">{stat.label}</p>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Right panel - login form */}
      <div className="w-full lg:w-[480px] bg-white flex flex-col justify-center p-8 lg:p-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-primary-600 rounded-xl flex items-center justify-center">
              <Heart size={16} className="text-white" />
            </div>
            <span className="font-display font-700 text-surface-900">MedCore HMS</span>
          </div>

          <h2 className="text-3xl font-display font-700 text-surface-900 mb-1">Welcome back</h2>
          <p className="text-surface-500 mb-8">Sign in to your account to continue</p>

          {/* Demo role buttons */}
          <div className="flex gap-2 mb-6">
            {(['admin', 'doctor', 'patient'] as const).map((role) => (
              <button
                key={role}
                type="button"
                onClick={() => fillDemo(role)}
                className="flex-1 py-1.5 text-xs font-medium rounded-lg border border-surface-200 
                           text-surface-600 hover:bg-surface-50 capitalize transition-colors"
              >
                {role}
              </button>
            ))}
          </div>
          <p className="text-xs text-surface-400 mb-6 text-center">↑ Click to fill demo credentials</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="form-group">
              <label className="label">Email Address</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input pl-10"
                  placeholder="you@hospital.com"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="label">Password</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input pl-10 pr-10"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-surface-400 hover:text-surface-600"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full py-3 mt-2 text-base"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signing in...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  Sign In <ArrowRight size={16} />
                </span>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-surface-500 mt-6">
            New patient?{' '}
            <Link to="/register" className="text-primary-600 font-medium hover:text-primary-700">
              Create an account
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  )
}
