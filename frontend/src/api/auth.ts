import { api } from './client'

export type User = {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
}

export type LoginResponse = {
  access_token: string
  token_type: string
  user: User
}

export async function login(email: string, password: string) {
  const body = new URLSearchParams()
  body.set('username', email)
  body.set('password', password)

  const { data } = await api.post<LoginResponse>('/auth/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export async function register(payload: {
  username: string
  email: string
  password: string
}) {
  const { data } = await api.post<User>('/auth/register', payload)
  return data
}

export async function getMe() {
  const { data } = await api.get<User>('/auth/me')
  return data
}
