import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export type ApiEnvelope<T> = {
  status: 'success' | 'error'
  generated_at: string
  data: T
  error?: { message: string; details?: unknown }
}

export function unwrapData<T>(payload: ApiEnvelope<T>): T {
  if (payload.status !== 'success') {
    throw new Error(payload.error?.message || 'Request failed')
  }
  return payload.data
}
