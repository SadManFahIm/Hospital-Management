import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Heart, Mail, Lock, User, Phone, ArrowRight } from 'lucide-react'
import { authAPI } from '@/services/api'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', username: '', password: '' })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      await authAPI.register({ ...form, role: 'patient' })
      toast.success('Account created! Please log in.')
      navigate('/login')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-surface-50 flex items-center justify-center p-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Heart size={22} className="text-white" />
          </div>
          <h1 className="text-2xl font-display font-700 text-surface-900">Create Account</h1>
          <p className="text-surface-500 text-sm mt-1">Register as a new patient</p>
        </div>

        <div className="card p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="form-group">
                <label className="label">First Name</label>
                <input value={form.first_name} onChange={e => setForm({...form, first_name: e.target.value})} className="input" placeholder="John" required />
              </div>
              <div className="form-group">
                <label className="label">Last Name</label>
                <input value={form.last_name} onChange={e => setForm({...form, last_name: e.target.value})} className="input" placeholder="Doe" required />
              </div>
            </div>
            <div className="form-group">
              <label className="label">Email</label>
              <div className="relative">
                <Mail size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400" />
                <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} className="input pl-10" placeholder="you@email.com" required />
              </div>
            </div>
            <div className="form-group">
              <label className="label">Username</label>
              <div className="relative">
                <User size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400" />
                <input value={form.username} onChange={e => setForm({...form, username: e.target.value})} className="input pl-10" placeholder="johndoe" required />
              </div>
            </div>
            <div className="form-group">
              <label className="label">Password</label>
              <div className="relative">
                <Lock size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400" />
                <input type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} className="input pl-10" placeholder="Min 8 characters" minLength={8} required />
              </div>
            </div>
            <button type="submit" disabled={isLoading} className="btn-primary w-full py-3 text-base mt-2">
              {isLoading ? <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Creating account...</span>
                : <span className="flex items-center gap-2">Create Account <ArrowRight size={16} /></span>}
            </button>
          </form>

          <p className="text-center text-sm text-surface-500 mt-4">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 font-medium hover:text-primary-700">Sign in</Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
