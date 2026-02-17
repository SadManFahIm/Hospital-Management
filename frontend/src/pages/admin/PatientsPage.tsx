import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Plus, Search, UserRound, Phone, Activity, Bed, HeartPulse, Trash2, Eye } from 'lucide-react'
import { patientsAPI } from '@/services/api'
import toast from 'react-hot-toast'
import clsx from 'clsx'

const mockPatients = [
  { id: 1, user: { first_name: 'John', last_name: 'Doe', email: 'john@email.com', is_approved: true, role: 'patient', is_active: true, username: 'john', created_at: '', id: 10 }, mobile: '01711111111', symptoms: 'Chest pain, shortness of breath', is_admitted: true, admit_date: '2026-02-10', blood_group: 'B+', user_id: 10, created_at: '' },
  { id: 2, user: { first_name: 'Maria', last_name: 'Garcia', email: 'maria@email.com', is_approved: true, role: 'patient', is_active: true, username: 'maria', created_at: '', id: 11 }, mobile: '01811111111', symptoms: 'Fever, fatigue', is_admitted: false, admit_date: null, blood_group: 'O+', user_id: 11, created_at: '' },
  { id: 3, user: { first_name: 'Ahmed', last_name: 'Khan', email: 'ahmed@email.com', is_approved: true, role: 'patient', is_active: true, username: 'ahmed', created_at: '', id: 12 }, mobile: '01911111111', symptoms: 'Knee pain', is_admitted: true, admit_date: '2026-02-14', blood_group: 'A+', user_id: 12, created_at: '' },
  { id: 4, user: { first_name: 'Fatima', last_name: 'Begum', email: 'fatima@email.com', is_approved: true, role: 'patient', is_active: true, username: 'fatima', created_at: '', id: 13 }, mobile: '01511111111', symptoms: 'Headache, dizziness', is_admitted: false, admit_date: null, blood_group: 'AB-', user_id: 13, created_at: '' },
  { id: 5, user: { first_name: 'Robert', last_name: 'Wilson', email: 'robert@email.com', is_approved: true, role: 'patient', is_active: true, username: 'robert', created_at: '', id: 14 }, mobile: '01611111111', symptoms: 'Back pain', is_admitted: false, admit_date: null, blood_group: 'O-', user_id: 14, created_at: '' },
]

export default function PatientsPage() {
  const [search, setSearch] = useState('')
  const [filterAdmit, setFilterAdmit] = useState<'all' | 'admitted' | 'outpatient'>('all')
  const queryClient = useQueryClient()

  const { data: patients = mockPatients } = useQuery({
    queryKey: ['patients'],
    queryFn: async () => {
      try {
        const { data } = await patientsAPI.list()
        return data
      } catch {
        return mockPatients
      }
    },
  })

  const admitMutation = useMutation({
    mutationFn: (id: number) => patientsAPI.admit(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['patients'] }); toast.success('Patient admitted') },
    onError: () => toast.error('Action failed'),
  })

  const dischargeMutation = useMutation({
    mutationFn: (id: number) => patientsAPI.discharge(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['patients'] }); toast.success('Patient discharged') },
    onError: () => toast.error('Action failed'),
  })

  const filtered = patients.filter((p: any) => {
    const name = `${p.user.first_name} ${p.user.last_name}`.toLowerCase()
    const matchSearch = name.includes(search.toLowerCase()) || p.symptoms?.toLowerCase().includes(search.toLowerCase())
    const matchFilter = filterAdmit === 'all' ? true : filterAdmit === 'admitted' ? p.is_admitted : !p.is_admitted
    return matchSearch && matchFilter
  })

  const bloodGroupColors: Record<string, string> = {
    'A+': 'bg-red-50 text-red-600', 'A-': 'bg-red-50 text-red-700',
    'B+': 'bg-orange-50 text-orange-600', 'B-': 'bg-orange-50 text-orange-700',
    'O+': 'bg-blue-50 text-blue-600', 'O-': 'bg-blue-50 text-blue-700',
    'AB+': 'bg-purple-50 text-purple-600', 'AB-': 'bg-purple-50 text-purple-700',
  }

  return (
    <div className="space-y-5">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="flex items-start justify-between">
        <div className="page-header mb-0">
          <h1 className="page-title">Patients</h1>
          <p className="page-subtitle">Manage patient records and admissions</p>
        </div>
        <button className="btn-primary">
          <Plus size={16} />
          Add Patient
        </button>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Total', value: patients.length, icon: <UserRound size={16} />, color: 'bg-blue-50 text-blue-600' },
          { label: 'Admitted', value: patients.filter((p: any) => p.is_admitted).length, icon: <Bed size={16} />, color: 'bg-amber-50 text-amber-600' },
          { label: 'Outpatient', value: patients.filter((p: any) => !p.is_admitted).length, icon: <Activity size={16} />, color: 'bg-emerald-50 text-emerald-600' },
        ].map((s) => (
          <div key={s.label} className="card p-4 flex items-center gap-3">
            <span className={clsx('w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0', s.color)}>{s.icon}</span>
            <div><p className="text-xl font-display font-700 text-surface-900">{s.value}</p><p className="text-xs text-surface-500">{s.label}</p></div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="card p-3 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" />
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or symptoms..." className="input pl-9 py-2" />
        </div>
        <div className="flex gap-2">
          {(['all', 'admitted', 'outpatient'] as const).map((f) => (
            <button key={f} onClick={() => setFilterAdmit(f)}
              className={clsx('px-3 py-2 rounded-xl text-sm font-medium capitalize transition-colors',
                filterAdmit === f ? 'bg-primary-600 text-white' : 'bg-surface-100 text-surface-600 hover:bg-surface-200')}>
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>Patient</th>
              <th>Blood Group</th>
              <th>Symptoms</th>
              <th>Contact</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((patient: any, i: number) => (
              <motion.tr key={patient.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.04 }}>
                <td>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-emerald-600 rounded-xl flex items-center justify-center text-white text-xs font-bold">
                      {patient.user.first_name[0]}{patient.user.last_name[0]}
                    </div>
                    <div>
                      <p className="font-medium text-surface-900 text-sm">{patient.user.first_name} {patient.user.last_name}</p>
                      <p className="text-xs text-surface-400">{patient.user.email}</p>
                    </div>
                  </div>
                </td>
                <td>
                  <span className={clsx('text-xs px-2 py-1 rounded-lg font-bold', bloodGroupColors[patient.blood_group] || 'bg-surface-100 text-surface-600')}>
                    {patient.blood_group || 'N/A'}
                  </span>
                </td>
                <td><p className="text-sm text-surface-600 max-w-[180px] truncate">{patient.symptoms || '—'}</p></td>
                <td className="text-sm text-surface-600">{patient.mobile}</td>
                <td>
                  {patient.is_admitted ? (
                    <span className="badge badge-warning"><Bed size={10} />Admitted</span>
                  ) : (
                    <span className="badge badge-success"><Activity size={10} />Outpatient</span>
                  )}
                </td>
                <td>
                  <div className="flex items-center gap-1.5">
                    <button className="btn-ghost py-1 px-2 text-xs"><Eye size={13} /></button>
                    {patient.is_admitted ? (
                      <button onClick={() => dischargeMutation.mutate(patient.id)} className="btn-secondary py-1 px-2 text-xs">Discharge</button>
                    ) : (
                      <button onClick={() => admitMutation.mutate(patient.id)} className="btn-primary py-1 px-2 text-xs">Admit</button>
                    )}
                  </div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center py-12 text-surface-400">
            <UserRound size={36} className="mx-auto mb-2 opacity-30" />
            <p>No patients found</p>
          </div>
        )}
      </div>
    </div>
  )
}
