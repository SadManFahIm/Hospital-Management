import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

// Auth Pages
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'

// Layout
import DashboardLayout from '@/components/layout/DashboardLayout'

// Admin Pages
import AdminDashboard from '@/pages/admin/AdminDashboard'
import DoctorsPage from '@/pages/admin/DoctorsPage'
import PatientsPage from '@/pages/admin/PatientsPage'
import AppointmentsPage from '@/pages/admin/AppointmentsPage'

// Doctor Pages
import DoctorDashboard from '@/pages/doctor/DoctorDashboard'
import DoctorAppointments from '@/pages/doctor/DoctorAppointments'
import DoctorPatients from '@/pages/doctor/DoctorPatients'

// Patient Pages
import PatientDashboard from '@/pages/patient/PatientDashboard'
import PatientAppointments from '@/pages/patient/PatientAppointments'
import PatientDoctors from '@/pages/patient/PatientDoctors'

// Public
import LandingPage from '@/pages/LandingPage'

function PrivateRoute({ children, roles }: { children: React.ReactNode; roles?: string[] }) {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (roles && user && !roles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />
  }
  return <>{children}</>
}

function RoleRedirect() {
  const { user } = useAuthStore()
  if (!user) return <Navigate to="/login" replace />
  if (user.role === 'admin') return <Navigate to="/admin/dashboard" replace />
  if (user.role === 'doctor') return <Navigate to="/doctor/dashboard" replace />
  return <Navigate to="/patient/dashboard" replace />
}

export default function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route
        path="/login"
        element={isAuthenticated ? <RoleRedirect /> : <LoginPage />}
      />
      <Route
        path="/register"
        element={isAuthenticated ? <RoleRedirect /> : <RegisterPage />}
      />

      {/* Dashboard redirect */}
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <RoleRedirect />
          </PrivateRoute>
        }
      />

      {/* Admin Routes */}
      <Route
        path="/admin"
        element={
          <PrivateRoute roles={['admin']}>
            <DashboardLayout role="admin" />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="doctors" element={<DoctorsPage />} />
        <Route path="patients" element={<PatientsPage />} />
        <Route path="appointments" element={<AppointmentsPage />} />
      </Route>

      {/* Doctor Routes */}
      <Route
        path="/doctor"
        element={
          <PrivateRoute roles={['doctor']}>
            <DashboardLayout role="doctor" />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<DoctorDashboard />} />
        <Route path="appointments" element={<DoctorAppointments />} />
        <Route path="patients" element={<DoctorPatients />} />
      </Route>

      {/* Patient Routes */}
      <Route
        path="/patient"
        element={
          <PrivateRoute roles={['patient']}>
            <DashboardLayout role="patient" />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<PatientDashboard />} />
        <Route path="appointments" element={<PatientAppointments />} />
        <Route path="doctors" element={<PatientDoctors />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
