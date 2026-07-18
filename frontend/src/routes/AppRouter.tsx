import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from '@/routes/ProtectedRoute'
import { MainLayout } from '@/layouts/MainLayout'
import { Login } from '@/pages/Login/Login'
import { Register } from '@/pages/Register/Register'
import { Dashboard } from '@/pages/Dashboard/Dashboard'
import { Chat } from '@/pages/Chat/Chat'
import { Narrative } from '@/pages/Narrative/Narrative'
import { Graph } from '@/pages/Graph/Graph'
import { Timeline } from '@/pages/Timeline/Timeline'
import { Evaluation } from '@/pages/Evaluation/Evaluation'
import { Reports } from '@/pages/Reports/Reports'
import { Settings } from '@/pages/Settings/Settings'

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/narratives" element={<Narrative />} />
            <Route path="/graph" element={<Graph />} />
            <Route path="/timeline" element={<Timeline />} />
            <Route path="/evaluation" element={<Evaluation />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
