import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { CalendarDays, Search, CheckCircle, XCircle, Clock, Filter } from 'lucide-react'
import { appointmentsAPI } from '@/services/api'
import toast from 'react-hot-toast'
import clsx from 'clsx'

const mockAppointments = [
  { id: 1, patient: { user: { first_name: 'John', last_name: 'Doe' } }, doctor: { user: { first_name: 'Sarah', last_name: 'Johnson' }, department: 'Cardiologist' }, appointment_date: '2026-02-18', appointment_time: '10:00 AM', description: 'Routine checkup', status: 'pending', created_at: '' },
  { id: 2, patient: { user: { first_name: 'Maria', last_name: 'Garcia' } }, doctor: { user: { first_name: 'Rahim', last_name: 'Chowdhury' }, department: 'Neurologist' }, appointment_date: '2026-02-18', appointment_time: '11:30 AM', description: 'Follow-up consultation', status: 'approved', created_at: '' },
  { id: 3, patient: { user: { first_name: 'Ahmed', last_name: 'Khan' } }, doctor: { user: { first_name: 'Priya', last_name: 'Sharma' }, department: 'Orthopedic' }, appointment_date: '2026-02-17', appointment_time: '02:00 PM', description: 'Knee pain consultation', status: 'completed', created_at: '' },
  { id: 4, patient: { user: { first_name: 'Fatima', last_name: 'Begum' } }, doctor: { user: { first_name: 'Kabir', last_name: 'Islam' }, department: 'Psychiatrist' }, appointment_date: '2026-02-19', appointment_time: '09:00 AM', description: 'Initial assessment', status: 'pending', created_at: '' },
  { id: 5, patient: { user: { first_name: 'Robert', last_name: 'Wilson' } }, doctor: { user: { first_name: 'Nasrin', last_name: 'Begum' }, department: 'Dermatologist' }, appointment_date: '2026-02-20', appointment_time: '03:30 PM', description: 'Skin rash checkup', status: 'cancelled', created_at: '' },
]

const statusConfig = {
  pending: { label: 'Pending', class: 'badge-warning', icon: <Clock size={10} /> },
  approved: { label: 'Approved', class: 'badge-info', icon: <CheckCircle size={10} /> },
  completed: { label: 'Completed', class: 'badge-success', icon: <CheckCircle size={10} /> },
  cancelled: { label: 'Cancelled', class: 'badge-danger', icon: <XCircle size={10} /> },
}

export default function AppointmentsPage() {
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const queryClient = useQueryClient()

  const { data: appointments = mockAppointments } = useQuery({
    queryKey: ['appointments'],
    queryFn: async () => {
      try {
        const { data } = await appointmentsAPI.list()
        return data
      } catch { return mockAppointments }
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      appointmentsAPI.update(id, { status }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['appointments'] }); toast.success('Appointment updated') },
    onError: () => toast.error('Update failed'),
  })

  const filtered = appointments.filter((a: any) => {
    const name = `${a.patient?.user?.first_name} ${a.patient?.user?.last_name}`.toLowerCase()
    const doc = `${a.doctor?.user?.first_name} ${a.doctor?.user?.last_name}`.toLowerCase()
    const matchSearch = name.includes(search.toLowerCase()) || doc.includes(search.toLowerCase())
    const matchStatus = filterStatus === 'all' || a.status === filterStatus
    return matchSearch && matchStatus
  })

  const statusCounts = {
    pending: appointments.filter((a: any) => a.status === 'pending').length,
    approved: appointments.filter((a: any) => a.status === 'approved').length,
    completed: appointments.filter((a: any) => a.status === 'completed').length,
  }

  return (
    <div className="space-y-5">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="page-header">
        <h1 className="page-title">Appointments</h1>
        <p className="page-subtitle">View and manage all hospital appointments</p>
      </motion.div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Pending', count: statusCounts.pending, color: 'bg-amber-50 text-amber-600 border-amber-200' },
          { label: 'Approved', count: statusCounts.approved, color: 'bg-blue-50 text-blue-600 border-blue-200' },
          { label: 'Completed', count: statusCounts.completed, color: 'bg-emerald-50 text-emerald-600 border-emerald-200' },
        ].map(s => (
          <div key={s.label} className={clsx('card p-4 border', s.color)}>
            <p className="text-2xl font-display font-700">{s.count}</p>
            <p className="text-xs font-medium mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="card p-3 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" />
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search patients or doctors..." className="input pl-9 py-2" />
        </div>
        <div className="flex gap-2 flex-wrap">
          {['all', 'pending', 'approved', 'completed', 'cancelled'].map((s) => (
            <button key={s} onClick={() => setFilterStatus(s)}
              className={clsx('px-3 py-2 rounded-xl text-xs font-medium capitalize transition-colors',
                filterStatus === s ? 'bg-primary-600 text-white' : 'bg-surface-100 text-surface-600 hover:bg-surface-200')}>
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Date & Time</th>
              <th>Description</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((appt: any, i: number) => {
              const sc = statusConfig[appt.status as keyof typeof statusConfig]
              return (
                <motion.tr key={appt.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.04 }}>
                  <td className="text-surface-400 font-mono text-xs">#{appt.id}</td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 bg-emerald-500 rounded-lg flex items-center justify-center text-white text-xs font-bold">
                        {appt.patient?.user?.first_name?.[0]}
                      </div>
                      <span className="text-sm font-medium text-surface-800">
                        {appt.patient?.user?.first_name} {appt.patient?.user?.last_name}
                      </span>
                    </div>
                  </td>
                  <td>
                    <p className="text-sm text-surface-800">Dr. {appt.doctor?.user?.first_name} {appt.doctor?.user?.last_name}</p>
                    <p className="text-xs text-surface-400">{appt.doctor?.department}</p>
                  </td>
                  <td>
                    <p className="text-sm font-medium text-surface-800">{appt.appointment_date}</p>
                    <p className="text-xs text-surface-400">{appt.appointment_time}</p>
                  </td>
                  <td className="max-w-[150px]">
                    <p className="text-sm text-surface-600 truncate">{appt.description}</p>
                  </td>
                  <td><span className={clsx('badge', sc?.class)}>{sc?.icon}{sc?.label}</span></td>
                  <td>
                    <div className="flex gap-1.5">
                      {appt.status === 'pending' && (
                        <>
                          <button onClick={() => updateMutation.mutate({ id: appt.id, status: 'approved' })}
                            className="btn-primary py-1 px-2 text-xs">
                            <CheckCircle size={12} /> Approve
                          </button>
                          <button onClick={() => updateMutation.mutate({ id: appt.id, status: 'cancelled' })}
                            className="btn-danger py-1 px-2 text-xs">
                            <XCircle size={12} />
                          </button>
                        </>
                      )}
                      {appt.status === 'approved' && (
                        <button onClick={() => updateMutation.mutate({ id: appt.id, status: 'completed' })}
                          className="btn-secondary py-1 px-2 text-xs">
                          Complete
                        </button>
                      )}
                    </div>
                  </td>
                </motion.tr>
              )
            })}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center py-12 text-surface-400">
            <CalendarDays size={36} className="mx-auto mb-2 opacity-30" />
            <p>No appointments found</p>
          </div>
        )}
      </div>
    </div>
  )
}
