import { Bot, ChartColumn, FolderCog, PieChart, ReceiptText, Wallet2 } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: ChartColumn },
  { to: '/assets', label: 'My Assets', icon: Wallet2 },
  { to: '/accounting', label: 'Accounting', icon: ReceiptText },
  { to: '/portfolio', label: 'Portfolio', icon: PieChart },
  { to: '/ai-advisor', label: 'AI Advisor', icon: Bot },
  { to: '/settings', label: 'Settings', icon: FolderCog },
]

function Sidebar() {
  return (
    <aside className="flex h-screen w-[250px] flex-col border-r border-white/10 bg-shell px-4 py-6 text-white">
      <div className="mb-9 rounded-xl border border-white/20 bg-white/5 px-4 py-3">
        <p className="text-xs uppercase tracking-[0.24em] text-teal-300">Wealth</p>
        <p className="font-display text-lg font-semibold">Wellness Hub</p>
      </div>

      <nav className="space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `sidebar-item ${isActive ? 'sidebar-item-active text-slate-900' : ''}`
              }
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      <div className="mt-auto rounded-xl border border-white/15 bg-gradient-to-br from-teal-400/25 to-blue-500/25 p-4">
        <p className="font-display text-sm">Portfolio Engine</p>
        <p className="mt-1 text-xs text-slate-100/80">Connected to your Auth + Assets MVP.</p>
      </div>
    </aside>
  )
}

export default Sidebar
