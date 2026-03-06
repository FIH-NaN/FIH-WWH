import { Navigate, Route, Routes } from 'react-router-dom'

import AppShell from './layout/AppShell.tsx'
import ProtectedRoute from './layout/ProtectedRoute.tsx'

import AdvisorPage from './pages/AdvisorPage.tsx'
import AssetsPage from './pages/AssetsPage.tsx'
import DashboardPage from './pages/DashboardPage.tsx'
import LoginPage from './pages/LoginPage.tsx'
import PortfolioPage from './pages/PortfolioPage.tsx'
import RegisterPage from './pages/RegisterPage.tsx'
import SettingsPage from './pages/SettingsPage.tsx'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/assets" element={<AssetsPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/ai-advisor" element={<AdvisorPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
