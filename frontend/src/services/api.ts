import axios from 'axios'
import { useAuthStore } from '@/store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor - attach token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - handle 401 with token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refreshToken = useAuthStore.getState().refreshToken
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          useAuthStore.getState().setAuth(data.user, data.access_token, data.refresh_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return api(original)
        } catch {
          useAuthStore.getState().logout()
          window.location.href = '/login'
        }
      } else {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ─── Auth API ──────────────────────────────────────────────────────────────────
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (data: any) => api.post('/auth/register', data),
  logout: (refreshToken: string) => api.post('/auth/logout', { refresh_token: refreshToken }),
  me: () => api.get('/auth/me'),
  changePassword: (oldPassword: string, newPassword: string) =>
    api.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    }),
}

// ─── Doctors API ───────────────────────────────────────────────────────────────
export const doctorsAPI = {
  list: (params?: any) => api.get('/doctors', { params }),
  get: (id: number) => api.get(`/doctors/${id}`),
  create: (data: any) => api.post('/doctors', data),
  update: (id: number, data: any) => api.put(`/doctors/${id}`, data),
  approve: (id: number) => api.patch(`/doctors/${id}/approve`),
  delete: (id: number) => api.delete(`/doctors/${id}`),
  getPatients: (id: number) => api.get(`/doctors/${id}/patients`),
}

// ─── Patients API ──────────────────────────────────────────────────────────────
export const patientsAPI = {
  list: (params?: any) => api.get('/patients', { params }),
  get: (id: number) => api.get(`/patients/${id}`),
  create: (data: any) => api.post('/patients', data),
  update: (id: number, data: any) => api.put(`/patients/${id}`, data),
  admit: (id: number) => api.patch(`/patients/${id}/admit`),
  discharge: (id: number) => api.patch(`/patients/${id}/discharge`),
  delete: (id: number) => api.delete(`/patients/${id}`),
}

// ─── Appointments API ──────────────────────────────────────────────────────────
export const appointmentsAPI = {
  list: (params?: any) => api.get('/appointments', { params }),
  get: (id: number) => api.get(`/appointments/${id}`),
  create: (data: any) => api.post('/appointments', data),
  update: (id: number, data: any) => api.patch(`/appointments/${id}`, data),
  delete: (id: number) => api.delete(`/appointments/${id}`),
  approve: (id: number) => api.patch(`/appointments/${id}`, { status: 'approved' }),
}

// ─── Dashboard API ─────────────────────────────────────────────────────────────
export const dashboardAPI = {
  adminStats: () => api.get('/dashboard/stats'),
  doctorStats: () => api.get('/dashboard/doctor-stats'),
  patientStats: () => api.get('/dashboard/patient-stats'),
}

// ─── Discharge API ─────────────────────────────────────────────────────────────
export const dischargeAPI = {
  list: () => api.get('/discharge'),
  create: (data: any) => api.post('/discharge', data),
  get: (id: number) => api.get(`/discharge/${id}`),
}
