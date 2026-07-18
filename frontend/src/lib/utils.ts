import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(value: number | null | undefined) {
  if (value == null || Number.isNaN(value)) return '—'
  return new Intl.NumberFormat('en-US').format(value)
}

export function formatPercent(value: number | null | undefined, digits = 1) {
  if (value == null || Number.isNaN(value)) return '—'
  return `${(value * 100).toFixed(digits)}%`
}

export function formatScore(value: number | null | undefined, digits = 3) {
  if (value == null || Number.isNaN(value)) return '—'
  return value.toFixed(digits)
}

export function truncate(text: string | null | undefined, max = 72) {
  if (text == null) return ''
  const value = typeof text === 'string' ? text : String(text)
  return value.length > max ? `${value.slice(0, max).trim()}…` : value
}

export function formatDate(value?: string | null) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}
