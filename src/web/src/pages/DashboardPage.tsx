import { Sparkles, TrendingUp } from 'lucide-react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis } from 'recharts'
import { formatMoney } from '../lib/format'

const growthSeries = [
  { month: 'Jan', value: 148000 },
  { month: 'Feb', value: 152500 },
  { month: 'Mar', value: 155900 },
  { month: 'Apr', value: 161800 },
  { month: 'May', value: 169400 },
  { month: 'Jun', value: 173900 },
  { month: 'Jul', value: 181300 },
]

const kpis = [
  { label: 'Total Assets', value: '$181.3K' },
  { label: 'Crypto Allocation', value: '28%' },
  { label: 'Health Score', value: '85 / 100' },
  { label: '24h Return', value: '+2.41%' },
]

function DashboardPage() {
  return (
    <section className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <article key={kpi.label} className="glass-panel p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{kpi.label}</p>
            <p className="mt-2 font-display text-2xl text-slate-900">{kpi.value}</p>
          </article>
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[2fr_1fr]">
        <article className="glass-panel p-4">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Portfolio Growth</h2>
              <p className="text-sm text-slate-500">Smooth 6-month valuation trend</p>
            </div>
            <div className="inline-flex items-center gap-1 rounded-lg bg-green-50 px-2 py-1 text-xs font-semibold text-green-700">
              <TrendingUp size={13} />
              +18.6%
            </div>
          </div>

          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={growthSeries} margin={{ left: 8, right: 8, top: 10, bottom: 0 }}>
                <defs>
                  <linearGradient id="valueFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#14b8a6" stopOpacity={0.45} />
                    <stop offset="100%" stopColor="#14b8a6" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 12 }} />
                <Tooltip formatter={(value) => formatMoney(Number(value))} />
                <Area type="monotone" dataKey="value" stroke="#0f766e" strokeWidth={3} fill="url(#valueFill)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="rounded-2xl border border-transparent bg-white p-4 shadow-panel [background:linear-gradient(white,white)_padding-box,linear-gradient(135deg,#14b8a6,#2563eb)_border-box]">
          <div className="inline-flex items-center gap-2 rounded-lg bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
            <Sparkles size={13} />
            AI Insights
          </div>
          <h3 className="mt-3 font-display text-lg text-slate-900">Actionable Recommendations</h3>

          <div className="mt-4 space-y-3 text-sm text-slate-600">
            <p className="rounded-xl bg-slate-50 p-3">
              Your crypto concentration is elevated. Consider trimming 5-8% into diversified equity ETFs to reduce volatility.
            </p>
            <p className="rounded-xl bg-slate-50 p-3">
              A stronger cash buffer can improve liquidity resilience. Target 6 months of core expenses in highly liquid accounts.
            </p>
          </div>
        </article>
      </div>
    </section>
  )
}

export default DashboardPage
