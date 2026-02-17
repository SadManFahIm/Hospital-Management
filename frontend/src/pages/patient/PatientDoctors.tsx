import { Stethoscope } from 'lucide-react'
export default function PatientDoctors() {
  return <div className="page-header"><h1 className="page-title">Find Doctors</h1><p className="page-subtitle">Browse available doctors by specialty</p><div className="mt-6 card p-8 text-center text-surface-400"><Stethoscope size={40} className="mx-auto mb-3 opacity-30" /><p>Doctor directory with specialty filters</p></div></div>
}
