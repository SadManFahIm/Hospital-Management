import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus, Search, Filter, MoreHorizontal, CheckCircle,
  XCircle, Trash2, Eye, Stethoscope, Phone, MapPin, Star
} from 'lucide-react'
import { doctorsAPI } from '@/services/api'
import toast from 'react-hot-toast'
import clsx from 'clsx'

const mockDoctors = [
  { id: 1, user: { first_name: 'Sarah', last_name: 'Johnson', email: 'sarah@hospital.com', is_approved: true, role: 'doctor', is_active: true, username: 'sarah', created_at: '', id: 1 }, department: 'Cardiologist', mobile: '01712345678', experience_years: 12, consultation_fee: 1500, user_id: 1, created_at: '' },
  { id: 2, user: { first_name: 'Rahim', last_name: 'Chowdhury', email: 'rahim@hospital.com', is_approved: true, role: 'doctor', is_active: true, username: 'rahim', created_at: '', id: 2 }, department: 'Neurologist', mobile: '01812345678', experience_years: 8, consultation_fee: 1200, user_id: 2, created_at: '' },
  { id: 3, user: { first_name: 'Priya', last_name: 'Sharma', email: 'priya@hospital.com', is_approved: false, role: 'doctor', is_active: true, username: 'priya', created_at: '', id: 3 }, department: 'Pediatrician', mobile: '01912345678', experience_years: 5, consultation_fee: 1000, user_id: 3, created_at: '' },
  { id: 4, user: { first_name: 'Kabir', last_name: 'Islam', email: 'kabir@hospital.com', is_approved: true, role: 'doctor', is_active: true, username: 'kabir', created_at: '', id: 4 }, department: 'Orthopedic Surgeon', mobile: '01612345678', experience_years: 15, consultation_fee: 2000, user_id: 4, created_at: '' },
  { id: 5, user: { first_name: 'Nasrin', last_name: 'Begum', email: 'nasrin@hospital.com', is_approved: false, role: 'doctor', is_active: true, username: 'nasrin', created_at: '', id: 5 }, department: 'Dermatologist', mobile: '01512345678', experience_years: 7, consultation_fee: 900, user_id: 5, created_at: '' },
]

const deptColors: Record<string, string> = {
  Cardiologist: 'bg-red-50 text-red-600',
  Neurologist: 'bg-purple-50 text-purple-600',
  Pediatrician: 'bg-pink-50 text-pink-600',
  'Orthopedic Surgeon': 'bg-orange-50 text-orange-600',
  Dermatologist: 'bg-teal-50 text-teal-600',
  Psychiatrist: 'bg-indigo-50 text-indigo-600',
}

export default function DoctorsPage() {
  const [search, setSearch] = useState('')
  const [filterApproved, setFilterApproved] = useState<'all' | 'approved' | 'pending'>('all')
  const queryClient = useQueryClient()

  const { data: doctors = mockDoctors, isLoading } = useQuery({
    queryKey: ['doctors'],
    queryFn: async () => {
      try {
        const { data } = await doctorsAPI.list()
        return data
      } catch {
        return mockDoctors
      }
    },
  })

  const approveMutation = useMutation({
    mutationFn: (id: number) => doctorsAPI.approve(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctors'] })
      toast.success('Doctor approved successfully')
    },
    onError: () => toast.error('Failed to approve doctor'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => doctorsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctors'] })
      toast.success('Doctor removed')
    },
    onError: () => toast.error('Failed to delete'),
  })

  const filtered = doctors.filter((d: any) => {
    const name = `${d.user.first_name} ${d.user.last_name}`.toLowerCase()
    const matchSearch = name.includes(search.toLowerCase()) ||
      d.department?.toLowerCase().includes(search.toLowerCase())
    const matchFilter =
      filterApproved === 'all' ? true :
      filterApproved === 'approved' ? d.user.is_approved :
      !d.user.is_approved
    return matchSearch && matchFilter
  })

  return (
    <div className="space-y-5">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="flex items-start justify-between">
        <div className="page-header mb-0">
          <h1 className="page-title">Doctors</h1>
          <p className="page-subtitle">Manage medical staff and approvals</p>
        </div>
        <button className="btn-primary">
          <Plus size={16} />
          Add Doctor
        </button>
      </motion.div>

      {/* Filters */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}
        className="card p-3 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search doctors by name or department..."
            className="input pl-9 py-2"
          />
        </div>
        <div className="flex gap-2">
          {(['all', 'approved', 'pending'] as const).map((f) => (
            <button key={f}
              onClick={() => setFilterApproved(f)}
              className={clsx('px-3 py-2 rounded-xl text-sm font-medium capitalize transition-colors',
                filterApproved === f
                  ? 'bg-primary-600 text-white'
                  : 'bg-surface-100 text-surface-600 hover:bg-surface-200'
              )}>
              {f}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Doctors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <AnimatePresence>
          {filtered.map((doctor: any, i: number) => (
            <motion.div
              key={doctor.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ delay: i * 0.04 }}
              className="card-hover p-5"
            >
              {/* Card Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl 
                                  flex items-center justify-center text-white font-bold text-base shadow-sm">
                    {doctor.user.first_name[0]}{doctor.user.last_name[0]}
                  </div>
                  <div>
                    <h3 className="font-semibold text-surface-900 text-sm">
                      Dr. {doctor.user.first_name} {doctor.user.last_name}
                    </h3>
                    <span className={clsx(
                      'text-xs px-2 py-0.5 rounded-lg font-medium',
                      deptColors[doctor.department] || 'bg-surface-100 text-surface-600'
                    )}>
                      {doctor.department}
                    </span>
                  </div>
                </div>
                <span className={doctor.user.is_approved ? 'badge badge-success' : 'badge badge-warning'}>
                  {doctor.user.is_approved ? 'Active' : 'Pending'}
                </span>
              </div>

              {/* Details */}
              <div className="space-y-2 mb-4 text-sm text-surface-600">
                <div className="flex items-center gap-2">
                  <Phone size={13} className="text-surface-400 flex-shrink-0" />
                  <span>{doctor.mobile || 'N/A'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Star size={13} className="text-surface-400 flex-shrink-0" />
                  <span>{doctor.experience_years || 0} years experience</span>
                </div>
                <div className="flex items-center gap-2">
                  <Stethoscope size={13} className="text-surface-400 flex-shrink-0" />
                  <span>Consultation: ৳{doctor.consultation_fee || 0}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-3 border-t border-surface-100">
                <button className="btn-secondary flex-1 py-1.5 text-xs">
                  <Eye size={13} />
                  View
                </button>
                {!doctor.user.is_approved && (
                  <button
                    onClick={() => approveMutation.mutate(doctor.id)}
                    disabled={approveMutation.isPending}
                    className="btn-primary flex-1 py-1.5 text-xs"
                  >
                    <CheckCircle size={13} />
                    Approve
                  </button>
                )}
                <button
                  onClick={() => {
                    if (confirm(`Remove Dr. ${doctor.user.first_name}?`)) {
                      deleteMutation.mutate(doctor.id)
                    }
                  }}
                  className="btn-danger px-2.5 py-1.5 text-xs"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-12 text-surface-400">
          <Stethoscope size={40} className="mx-auto mb-3 opacity-30" />
          <p className="font-medium">No doctors found</p>
          <p className="text-sm">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  )
}
