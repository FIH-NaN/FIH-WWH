import { Menu } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'
import { listAssets } from '../services/assetsService'
import { useAuth } from '../state/AuthContext'
import Sidebar from './Sidebar'
import TopHeader from './TopHeader'

const FALLBACK_NET_WORTH = 245000

function AppShell() {
  const { token } = useAuth()
  const [netWorth, setNetWorth] = useState(FALLBACK_NET_WORTH)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    if (!token) {
      return
    }

    const fetchNetWorth = async () => {
      try {
        const response = await listAssets(token)
        const total = response.data.assets.reduce((sum, item) => sum + item.value, 0)
        setNetWorth(total || FALLBACK_NET_WORTH)
      } catch {
        setNetWorth(FALLBACK_NET_WORTH)
      }
    }

    const refresh = () => {
      void fetchNetWorth()
    }

    void fetchNetWorth()
    window.addEventListener('wwh:assets-updated', refresh)

    return () => {
      window.removeEventListener('wwh:assets-updated', refresh)
    }
  }, [token])

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[250px_1fr]">
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {sidebarOpen ? (
        <div className="fixed inset-0 z-40 bg-slate-900/40 lg:hidden" onClick={() => setSidebarOpen(false)}>
          <div className="h-full w-[250px]" onClick={(event) => event.stopPropagation()}>
            <Sidebar />
          </div>
        </div>
      ) : null}

      <main className="px-3 py-4 sm:px-6 sm:py-6">
        <button
          type="button"
          className="mb-3 inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 lg:hidden"
          onClick={() => setSidebarOpen(true)}
        >
          <Menu size={16} />
          Menu
        </button>

        <TopHeader netWorth={netWorth} />
        <Outlet />
      </main>
    </div>
  )
}

export default AppShell
