import { Users } from 'lucide-react'
export default function DoctorPatients() {
  return <div className="page-header"><h1 className="page-title">My Patients</h1><p className="page-subtitle">Patients assigned to you</p><div className="mt-6 card p-8 text-center text-surface-400"><Users size={40} className="mx-auto mb-3 opacity-30" /><p>Patient list for doctors</p></div></div>
}
