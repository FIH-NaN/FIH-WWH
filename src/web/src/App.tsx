import { useEffect, useMemo, useState, type FormEvent, type ReactElement } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import './App.css'
import { getAccounts, getAssetSummary, getAssets, login } from './services/api'

type AssetItem = {
  id?: number
  name: string
  category: string
  value: number
  currency: string
  liquid: boolean
}

type LiabilityItem = {
  name: string
  category: 'Mortgage' | 'Loan' | 'Credit Card' | 'Tax'
  outstanding: number
  monthlyPayment: number
  currency: string
}

type IncomeItem = {
  source: string
  type: 'Salary' | 'Dividend' | 'Freelance' | 'Rental'
  monthly: number
  currency: string
}

type ExpenseItem = {
  name: string
  category: 'Housing' | 'Food' | 'Transport' | 'Insurance' | 'Investment' | 'Other'
  monthly: number
  currency: string
  essential: boolean
}

type CashFlowItem = {
  date: string
  type: 'Inflow' | 'Outflow' | 'Transfer'
  category: string
  amount: number
  currency: string
}

type AccountItem = {
  id: number
  account_type: string
  provider: string
  name: string
  status: string
  last_synced?: string | null
}

const liabilities: LiabilityItem[] = [
  { name: 'Home Mortgage', category: 'Mortgage', outstanding: 175000, monthlyPayment: 1650, currency: 'USD' },
  { name: 'Education Loan', category: 'Loan', outstanding: 12000, monthlyPayment: 320, currency: 'USD' },
  { name: 'Card Balance', category: 'Credit Card', outstanding: 2800, monthlyPayment: 250, currency: 'USD' },
]

const incomes: IncomeItem[] = [
  { source: 'Base Salary', type: 'Salary', monthly: 7200, currency: 'USD' },
  { source: 'ETF Dividends', type: 'Dividend', monthly: 210, currency: 'USD' },
  { source: 'Consulting', type: 'Freelance', monthly: 900, currency: 'USD' },
]

const expenses: ExpenseItem[] = [
  { name: 'Mortgage Payment', category: 'Housing', monthly: 1650, currency: 'USD', essential: true },
  { name: 'Groceries', category: 'Food', monthly: 620, currency: 'USD', essential: true },
  { name: 'Transport', category: 'Transport', monthly: 340, currency: 'USD', essential: true },
  { name: 'Insurance', category: 'Insurance', monthly: 280, currency: 'USD', essential: true },
  { name: 'ETF Auto Invest', category: 'Investment', monthly: 1000, currency: 'USD', essential: false },
]

const cashFlows: CashFlowItem[] = [
  { date: '2026-03-01', type: 'Inflow', category: 'Salary', amount: 7200, currency: 'USD' },
  { date: '2026-03-02', type: 'Outflow', category: 'Mortgage', amount: 1650, currency: 'USD' },
  { date: '2026-03-03', type: 'Outflow', category: 'Groceries', amount: 155, currency: 'USD' },
  { date: '2026-03-03', type: 'Transfer', category: 'Broker Deposit', amount: 500, currency: 'USD' },
  { date: '2026-03-04', type: 'Inflow', category: 'Freelance', amount: 450, currency: 'USD' },
]

const formatMoney = (amount: number, currency = 'USD') =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(amount)

function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await login(email, password)
      const token = response.data?.data?.token
      if (!token) {
        alert('Login failed: token missing')
        return
      }
      localStorage.setItem('token', token)
      navigate('/')
    } catch (error) {
      console.error(error)
      alert('Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page" style={{ maxWidth: 520 }}>
      <header className="header">
        <div>
          <h1>Wealth Wellness Hub</h1>
          <p>Sign in to view your real-time dashboard.</p>
        </div>
      </header>

      <section className="panel">
        <form onSubmit={handleLogin} style={{ display: 'grid', gap: 12 }}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ padding: 10, borderRadius: 10, border: '1px solid #d1d5db' }}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ padding: 10, borderRadius: 10, border: '1px solid #d1d5db' }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              background: '#1f4ed8',
              color: '#fff',
              border: 0,
              borderRadius: 10,
              padding: '10px 12px',
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </section>
    </main>
  )
}

function DashboardPage() {
  const navigate = useNavigate()
  const [assets, setAssets] = useState<AssetItem[]>([])
  const [accounts, setAccounts] = useState<AccountItem[]>([])
  const [summaryTotalValue, setSummaryTotalValue] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true

    const load = async () => {
      setLoading(true)
      try {
        const [assetsResp, summaryResp, accountsResp] = await Promise.all([
          getAssets(),
          getAssetSummary(),
          getAccounts(),
        ])

        if (!mounted) return

        const apiAssets = (assetsResp.data?.data?.assets || []).map((a: any) => ({
          id: a.id,
          name: a.name,
          category: a.category || a.asset_type || 'Other',
          value: Number(a.value || 0),
          currency: a.currency || 'USD',
          liquid: ['cash', 'stock', 'fund', 'crypto'].includes(String(a.asset_type || '').toLowerCase()),
        }))

        setAssets(apiAssets)
        setSummaryTotalValue(Number(summaryResp.data?.data?.total_value || 0))
        setAccounts(accountsResp.data?.data || [])
      } catch (error) {
        console.error(error)
        alert('Failed to load dashboard data')
      } finally {
        if (mounted) setLoading(false)
      }
    }

    load()
    return () => {
      mounted = false
    }
  }, [])

  const totalAssetValue = useMemo(
    () => (summaryTotalValue !== null ? summaryTotalValue : assets.reduce((sum, item) => sum + item.value, 0)),
    [assets, summaryTotalValue],
  )
  const totalLiabilityValue = liabilities.reduce((sum, item) => sum + item.outstanding, 0)
  const totalMonthlyIncome = incomes.reduce((sum, item) => sum + item.monthly, 0)
  const totalMonthlyExpense = expenses.reduce((sum, item) => sum + item.monthly, 0)
  const monthlyNetCash = totalMonthlyIncome - totalMonthlyExpense
  const essentialExpenses = expenses
    .filter((expense) => expense.essential)
    .reduce((sum, item) => sum + item.monthly, 0)

  const assetCategoryTotals = assets.reduce<Record<string, number>>((acc, asset) => {
    acc[asset.category] = (acc[asset.category] ?? 0) + asset.value
    return acc
  }, {})

  const expenseCategoryTotals = expenses.reduce<Record<string, number>>((acc, expense) => {
    acc[expense.category] = (acc[expense.category] ?? 0) + expense.monthly
    return acc
  }, {})

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  if (loading) {
    return (
      <main className="page">
        <section className="panel">Loading dashboard...</section>
      </main>
    )
  }

  return (
    <main className="page">
      <header className="header">
        <div>
          <h1>Wealth Dashboard</h1>
          <p>Unified snapshot of assets, liabilities, cash flows, income, and expenses.</p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span className="pill">Live Data</span>
          <button
            onClick={handleLogout}
            style={{ background: '#fff', border: '1px solid #d1d5db', borderRadius: 999, padding: '8px 12px' }}
          >
            Logout
          </button>
        </div>
      </header>

      <section className="kpi-grid">
        <article className="kpi-card">
          <p className="kpi-label">Total Assets</p>
          <h2>{formatMoney(totalAssetValue)}</h2>
        </article>
        <article className="kpi-card">
          <p className="kpi-label">Total Liabilities</p>
          <h2>{formatMoney(totalLiabilityValue)}</h2>
        </article>
        <article className="kpi-card">
          <p className="kpi-label">Monthly Income</p>
          <h2>{formatMoney(totalMonthlyIncome)}</h2>
        </article>
        <article className="kpi-card">
          <p className="kpi-label">Monthly Expense</p>
          <h2>{formatMoney(totalMonthlyExpense)}</h2>
        </article>
        <article className="kpi-card accent">
          <p className="kpi-label">Monthly Net Cash Flow</p>
          <h2>{formatMoney(monthlyNetCash)}</h2>
          <small>{Math.round((essentialExpenses / totalMonthlyExpense) * 100)}% essential spending</small>
        </article>
      </section>

      <section className="grid-two">
        <article className="panel">
          <div className="panel-head">
            <h3>Assets</h3>
            <span>{assets.length} holdings</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Liquid</th>
                <th className="align-right">Value</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={String(asset.id || asset.name)}>
                  <td>{asset.name}</td>
                  <td>{asset.category}</td>
                  <td>{asset.liquid ? 'Yes' : 'No'}</td>
                  <td className="align-right">{formatMoney(asset.value, asset.currency)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mini-chart">
            {Object.entries(assetCategoryTotals).map(([category, value]) => (
              <div key={category} className="bar-row">
                <span>{category}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${(value / Math.max(totalAssetValue, 1)) * 100}%` }} />
                </div>
                <span>{formatMoney(value)}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-head">
            <h3>Connected Accounts</h3>
            <span>{accounts.length} active</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Provider</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {accounts.map((acc) => (
                <tr key={acc.id}>
                  <td>{acc.name}</td>
                  <td>{acc.account_type}</td>
                  <td>{acc.provider}</td>
                  <td>{acc.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
      </section>

      <section className="grid-two">
        <article className="panel">
          <div className="panel-head">
            <h3>Income</h3>
            <span>{formatMoney(totalMonthlyIncome)}/month</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Source</th>
                <th>Type</th>
                <th className="align-right">Monthly</th>
              </tr>
            </thead>
            <tbody>
              {incomes.map((income) => (
                <tr key={income.source}>
                  <td>{income.source}</td>
                  <td>{income.type}</td>
                  <td className="align-right">{formatMoney(income.monthly, income.currency)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>

        <article className="panel">
          <div className="panel-head">
            <h3>Expenses</h3>
            <span>{formatMoney(totalMonthlyExpense)}/month</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Essential</th>
                <th className="align-right">Monthly</th>
              </tr>
            </thead>
            <tbody>
              {expenses.map((expense) => (
                <tr key={expense.name}>
                  <td>{expense.name}</td>
                  <td>{expense.category}</td>
                  <td>{expense.essential ? 'Yes' : 'No'}</td>
                  <td className="align-right">{formatMoney(expense.monthly, expense.currency)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mini-chart">
            {Object.entries(expenseCategoryTotals).map(([category, value]) => (
              <div key={category} className="bar-row">
                <span>{category}</span>
                <div className="bar-track">
                  <div className="bar-fill expense" style={{ width: `${(value / totalMonthlyExpense) * 100}%` }} />
                </div>
                <span>{formatMoney(value)}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="panel">
        <div className="panel-head">
          <h3>Recent Cash Flows</h3>
          <span>{cashFlows.length} records</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Category</th>
              <th className="align-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {cashFlows.map((flow, index) => (
              <tr key={`${flow.date}-${flow.category}-${index}`}>
                <td>{flow.date}</td>
                <td>
                  <span className={`tag ${flow.type.toLowerCase()}`}>{flow.type}</span>
                </td>
                <td>{flow.category}</td>
                <td className="align-right">{formatMoney(flow.amount, flow.currency)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  )
}

function ProtectedRoute({ children }: { children: ReactElement }) {
  const token = localStorage.getItem('token')
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  )
}

export default App
