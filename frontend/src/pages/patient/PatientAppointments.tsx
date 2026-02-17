import { CalendarDays } from 'lucide-react'
export default function PatientAppointments() {
  return <div className="page-header"><h1 className="page-title">My Appointments</h1><p className="page-subtitle">Book and view your appointments</p><div className="mt-6 card p-8 text-center text-surface-400"><CalendarDays size={40} className="mx-auto mb-3 opacity-30" /><p>Book new appointments and view history</p></div></div>
}
