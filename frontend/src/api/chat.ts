import { api } from './client'
import type { User } from './auth'

export type Message = {
  id: number
  role: string
  content: string
  confidence?: number | null
  created_at: string
}

export type Conversation = {
  id: number
  user_id: number
  title: string
  created_at: string
  updated_at: string
  messages: Message[]
}

export type QueryResponse = {
  answer: string
  retrieval_stats: Record<string, unknown>
  conversation_id: number
}

export async function listConversations() {
  const { data } = await api.get<Conversation[]>('/conversations/')
  return data
}

export async function getConversation(id: number) {
  const { data } = await api.get<Conversation>(`/conversations/${id}`)
  return data
}

export async function createConversation(title: string) {
  const { data } = await api.post<Conversation>('/conversations/', { title })
  return data
}

export async function deleteConversation(id: number) {
  const { data } = await api.delete<{ message: string }>(`/conversations/${id}`)
  return data
}

export async function askQuestion(question: string, conversationId?: number | null) {
  const { data } = await api.post<QueryResponse>('/query/', {
    question,
    conversation_id: conversationId ?? null,
  })
  return data
}

export type { User }
