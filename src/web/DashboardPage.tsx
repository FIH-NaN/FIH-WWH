import { Sparkles, TrendingUp, Send, Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formatMoney } from '../lib/format'
import { dashboardService } from '../services/dashboardService'
import type { BalanceSheet, IncomeStatement, AIAdvice } from '../services/dashboardService'
import { useAuth } from '../state/AuthContext'

function DashboardPage() {
  const { token } = useAuth()
  const [balanceSheet, setBalanceSheet] = useState<BalanceSheet | null>(null)
  const [incomeStatement, setIncomeStatement] = useState<IncomeStatement | null>(null)
  const [totalIncome, setTotalIncome] = useState<number>(0)
  const [totalExpense, setTotalExpense] = useState<number>(0)
  const [aiAdvice, setAiAdvice] = useState<AIAdvice | null>(null)
  const [loading, setLoading] = useState(true)
  const [promptInput, setPromptInput] = useState('')
  const [submittingPrompt, setSubmittingPrompt] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      if (!token) return
      setLoading(true)
      try {
        const [bs, is, income, expense, advice] = await Promise.all([
          dashboardService.getBalanceSheet(token),
          dashboardService.getIncomeStatement(token),
          dashboardService.getTotalIncome(token),
          dashboardService.getTotalExpense(token),
          dashboardService.getDefaultAdvice(token),
        ])
        setBalanceSheet(bs)
        setIncomeStatement(is)
        setTotalIncome(income)
        setTotalExpense(expense)
        setAiAdvice(advice)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    void fetchData()
  }, [token])

  const handlePromptSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!token || !promptInput.trim()) return

    setSubmittingPrompt(true)
    try {
      const advice = await dashboardService.getPromptBasedAdvice(token, promptInput.trim())
      setAiAdvice(advice)
      setPromptInput('')
    } catch (error) {
      console.error('Error fetching AI advice:', error)
    } finally {
      setSubmittingPrompt(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-slate-500">Loading dashboard...</div>
      </div>
    )
  }

  const netWorth = balanceSheet?.net_worth ?? 0
  const savingsRate = totalIncome > 0 ? ((totalIncome - totalExpense) / totalIncome) * 100 : 0

  // Prepare data for stacked bar chart (Balance Sheet)
  const balanceSheetData = [
    {
      name: 'Assets',
      ...Object.fromEntries(balanceSheet?.assets.map(a => [a.category, a.amount]) ?? []),
    },
    {
      name: 'Liabilities',
      ...Object.fromEntries(balanceSheet?.liabilities.map(l => [l.category, l.amount]) ?? []),
    },
  ]

  // Prepare data for income statement line chart
  const incomeStatementChartData = [
    ...(incomeStatement?.income_items.map(item => ({
      category: item.category,
      actual: item.actual,
      budgeted: item.budgeted,
      type: 'Income',
    })) ?? []),
    ...(incomeStatement?.expense_items.map(item => ({
      category: item.category,
      actual: item.actual,
      budgeted: item.budgeted,
      type: 'Expense',
    })) ?? []),
  ]

  const assetColors = ['#14b8a6', '#2563eb', '#f59e0b', '#8b5cf6', '#10b981', '#ec4899']
  const liabilityColors = ['#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16']

  return (
    <section className="space-y-4">
      {/* KPIs */}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <article className="glass-panel p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Net Worth</p>
          <p className="mt-2 font-display text-2xl text-slate-900">{formatMoney(netWorth)}</p>
        </article>
        <article className="glass-panel p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Total Income</p>
          <p className="mt-2 font-display text-2xl text-slate-900">{formatMoney(totalIncome)}</p>
        </article>
        <article className="glass-panel p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Total Expenses</p>
          <p className="mt-2 font-display text-2xl text-slate-900">{formatMoney(totalExpense)}</p>
        </article>
        <article className="glass-panel p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Savings Rate</p>
          <p className="mt-2 font-display text-2xl text-slate-900">{savingsRate.toFixed(1)}%</p>
        </article>
      </div>

      <div className="grid gap-4 xl:grid-cols-[2fr_1fr]">
        {/* Balance Sheet */}
        <article className="glass-panel p-4">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Balance Sheet</h2>
            <p className="text-sm text-slate-500">Asset allocations vs liabilities</p>
          </div>

          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={balanceSheetData} margin={{ left: 20, right: 20, top: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 12 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
                <Tooltip formatter={(value) => formatMoney(Number(value))} />
                <Legend />
                {balanceSheet?.assets.map((asset, idx) => (
                  <Bar key={asset.category} dataKey={asset.category} stackId="a" fill={assetColors[idx % assetColors.length]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>

        {/* AI Insights */}
        <article className="rounded-2xl border border-transparent bg-white p-4 shadow-panel [background:linear-gradient(white,white)_padding-box,linear-gradient(135deg,#14b8a6,#2563eb)_border-box]">
          <div className="inline-flex items-center gap-2 rounded-lg bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
            <Sparkles size={13} />
            AI Insights
          </div>
          <h3 className="mt-3 font-display text-lg text-slate-900">Financial Advice</h3>

          <div className="mt-4 space-y-3">
            {aiAdvice && (
              <p className="rounded-xl bg-slate-50 p-3 text-sm text-slate-600">
                {aiAdvice.advice}
              </p>
            )}

            <form onSubmit={handlePromptSubmit} className="flex gap-2">
              <input
                type="text"
                value={promptInput}
                onChange={(e) => setPromptInput(e.target.value)}
                placeholder="Ask for advice..."
                className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none"
                disabled={submittingPrompt}
              />
              <button
                type="submit"
                disabled={submittingPrompt || !promptInput.trim()}
                className="rounded-lg bg-teal-600 px-3 py-2 text-white hover:bg-teal-700 disabled:opacity-50"
              >
                {submittingPrompt ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
              </button>
            </form>
          </div>
        </article>
      </div>

      {/* Income Statement */}
      <article className="glass-panel p-4">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Income Statement</h2>
            <p className="text-sm text-slate-500">Current month comparison vs budget</p>
          </div>
          <div className="inline-flex items-center gap-1 rounded-lg bg-green-50 px-2 py-1 text-xs font-semibold text-green-700">
            <TrendingUp size={13} />
            {formatMoney(incomeStatement?.remaining_balance ?? 0)} remaining
          </div>
        </div>

        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={incomeStatementChartData} margin={{ left: 20, right: 20, top: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="category" tick={{ fill: '#64748b', fontSize: 11 }} angle={-45} textAnchor="end" height={80} />
              <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
              <Tooltip formatter={(value) => formatMoney(Number(value))} />
              <Legend />
              <Line type="monotone" dataKey="actual" stroke="#14b8a6" strokeWidth={2} name="Actual" />
              <Line type="monotone" dataKey="budgeted" stroke="#94a3b8" strokeWidth={2} strokeDasharray="5 5" name="Budgeted" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </article>
    </section>
  )
}

export default DashboardPage
