import { Bell, LogOut, UserCircle2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { formatMoney } from '../lib/format'
import { useAuth } from '../state/AuthContext'

type Props = {
  netWorth: number
}

function TopHeader({ netWorth }: Props) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="glass-panel mb-6 flex h-16 items-center justify-end gap-3 px-4 sm:gap-5">
      <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-1 text-right">
        <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">Net Worth</p>
        <p className="font-display text-sm font-semibold text-slate-900">{formatMoney(netWorth)}</p>
      </div>

      <button
        type="button"
        className="grid size-9 place-items-center rounded-full border border-slate-200 bg-white text-slate-600 transition hover:bg-slate-100"
        aria-label="Notifications"
      >
        <Bell size={16} />
      </button>

      <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-2 py-1">
        <UserCircle2 className="text-slate-500" size={18} />
        <span className="max-w-28 truncate text-xs font-medium text-slate-700">{user?.name ?? 'Investor'}</span>
        <button
          type="button"
          className="grid size-7 place-items-center rounded-lg text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
          aria-label="Logout"
          onClick={() => {
            logout()
            navigate('/login', { replace: true })
          }}
        >
          <LogOut size={15} />
        </button>
      </div>
    </header>
  )
}

export default TopHeader
