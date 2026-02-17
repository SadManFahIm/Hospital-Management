import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Heart, ArrowRight, Stethoscope, Shield, BarChart3, Users, CheckCircle } from 'lucide-react'

const features = [
  { icon: <Stethoscope size={22} />, title: 'Smart Scheduling', desc: 'Effortless appointment booking with real-time doctor availability.' },
  { icon: <Shield size={22} />, title: 'RBAC Security', desc: 'Role-based access control for admins, doctors, and patients.' },
  { icon: <BarChart3 size={22} />, title: 'Analytics Dashboard', desc: 'Real-time insights into hospital operations and performance.' },
  { icon: <Users size={22} />, title: 'Patient Management', desc: 'Complete patient records, admissions, and discharge workflows.' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface-950 text-white overflow-hidden">
      {/* Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-primary-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-violet-600/8 rounded-full blur-3xl" />
      </div>

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-6 lg:px-12 py-5 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-primary-600 rounded-xl flex items-center justify-center">
            <Heart size={18} className="text-white" />
          </div>
          <span className="font-display font-700 text-white text-xl">MedCore <span className="text-primary-400">HMS</span></span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-surface-400 hover:text-white text-sm font-medium transition-colors">Sign in</Link>
          <Link to="/register" className="btn-primary text-sm">Get Started</Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 px-6 lg:px-12 pt-20 pb-24 text-center max-w-4xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-primary-950 border border-primary-800 rounded-full text-primary-400 text-xs font-medium mb-6">
            <span className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-pulse" />
            Version 2.0 — Modern Stack
          </span>
          <h1 className="text-5xl lg:text-7xl font-display font-800 leading-tight mb-6">
            Hospital Management
            <span className="block text-primary-400">Reimagined</span>
          </h1>
          <p className="text-surface-400 text-lg lg:text-xl leading-relaxed mb-10 max-w-2xl mx-auto">
            A fully modernized hospital management system with React frontend, FastAPI backend,
            JWT authentication, RBAC, and real-time analytics.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register" className="btn-primary text-base py-3 px-8">
              Start for Free <ArrowRight size={18} />
            </Link>
            <Link to="/login" className="bg-white/5 border border-white/10 text-white hover:bg-white/10 btn text-base py-3 px-8 rounded-xl">
              Sign In
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Features */}
      <section className="relative z-10 px-6 lg:px-12 py-16 max-w-6xl mx-auto">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((f, i) => (
            <motion.div key={f.title} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + i * 0.1 }}
              className="bg-white/5 border border-white/10 rounded-2xl p-5 hover:bg-white/8 transition-colors">
              <div className="w-10 h-10 bg-primary-600/20 rounded-xl flex items-center justify-center text-primary-400 mb-4">
                {f.icon}
              </div>
              <h3 className="font-display font-600 text-white mb-2">{f.title}</h3>
              <p className="text-sm text-surface-500 leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Tech Stack */}
      <section className="relative z-10 px-6 lg:px-12 py-12 border-t border-white/5">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-surface-600 text-sm mb-6">Built with modern technology</p>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-surface-500">
            {['React 18', 'TypeScript', 'FastAPI', 'SQLAlchemy', 'JWT Auth', 'Tailwind CSS', 'Zustand', 'React Query', 'Recharts', 'Framer Motion'].map(t => (
              <span key={t} className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-full">{t}</span>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
