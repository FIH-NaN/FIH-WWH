import { DollarSign, TrendingDown, TrendingUp } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Line, LineChart, ResponsiveContainer, Tooltip, CartesianGrid, XAxis, YAxis, Legend } from 'recharts'
import { formatMoney } from '../lib/format'
import { accountingService } from '../services/accountingService'
import type { MonthlyTransactions, TimeSeries } from '../services/accountingService'
import { useAuth } from '../state/AuthContext'

function AccountingPage() {
  const { token } = useAuth()
  const [incomeTransactions, setIncomeTransactions] = useState<MonthlyTransactions | null>(null)
  const [expenseTransactions, setExpenseTransactions] = useState<MonthlyTransactions | null>(null)
  const [incomeTimeSeries, setIncomeTimeSeries] = useState<TimeSeries | null>(null)
  const [expenseTimeSeries, setExpenseTimeSeries] = useState<TimeSeries | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      if (!token) return
      setLoading(true)
      try {
        const [income, expense, incomeSeries, expenseSeries] = await Promise.all([
          accountingService.getCurrentMonthIncome(token),
          accountingService.getCurrentMonthExpense(token),
          accountingService.getLastTwelveMonthsIncome(token),
          accountingService.getLastTwelveMonthsExpense(token),
        ])
        setIncomeTransactions(income)
        setExpenseTransactions(expense)
        setIncomeTimeSeries(incomeSeries)
        setExpenseTimeSeries(expenseSeries)
      } catch (error) {
        console.error('Error fetching accounting data:', error)
      } finally {
        setLoading(false)
      }
    }

    void fetchData()
  }, [token])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-slate-500">Loading accounting data...</div>
      </div>
    )
  }

  const netIncome = (incomeTransactions?.total ?? 0) - (expenseTransactions?.total ?? 0)
  const avgMonthlyIncome = incomeTimeSeries?.average ?? 0
  const avgMonthlyExpense = expenseTimeSeries?.average ?? 0

  // Combine time series data for chart
  const combinedTimeSeries = incomeTimeSeries?.data.map((item, idx) => ({
    date: item.date,
    income: item.amount,
    expense: expenseTimeSeries?.data[idx]?.amount ?? 0,
  })) ?? []

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-slate-900">Accounting</h1>
          <p className="mt-1 text-sm text-slate-500">Track income and expenses</p>
        </div>
        <div className={`inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-semibold ${netIncome >= 0 ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
          {netIncome >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
          Net: {formatMoney(netIncome)}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-3 sm:grid-cols-3">
        <article className="glass-panel p-4">
          <div className="flex items-center gap-2">
            <div className="rounded-full bg-green-100 p-2">
              <TrendingUp size={16} className="text-green-600" />
            </div>
            <div>
              <p className="text-xs text-slate-500">Total Income</p>
              <p className="font-display text-xl text-slate-900">{formatMoney(incomeTransactions?.total ?? 0)}</p>
            </div>
          </div>
        </article>

        <article className="glass-panel p-4">
          <div className="flex items-center gap-2">
            <div className="rounded-full bg-red-100 p-2">
              <TrendingDown size={16} className="text-red-600" />
            </div>
            <div>
              <p className="text-xs text-slate-500">Total Expenses</p>
              <p className="font-display text-xl text-slate-900">{formatMoney(expenseTransactions?.total ?? 0)}</p>
            </div>
          </div>
        </article>

        <article className="glass-panel p-4">
          <div className="flex items-center gap-2">
            <div className="rounded-full bg-blue-100 p-2">
              <DollarSign size={16} className="text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-slate-500">Balance</p>
              <p className={`font-display text-xl ${netIncome >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatMoney(netIncome)}
              </p>
            </div>
          </div>
        </article>
      </div>

      {/* Current Month Tables */}
      <div className="grid gap-4 xl:grid-cols-2">
        {/* Income Transactions */}
        <article className="glass-panel p-5">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Current Month Income</h2>
            <p className="text-sm text-slate-500">{incomeTransactions?.count ?? 0} transactions</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="pb-2 text-left text-xs font-semibold text-slate-600">Date</th>
                  <th className="pb-2 text-left text-xs font-semibold text-slate-600">Description</th>
                  <th className="pb-2 text-left text-xs font-semibold text-slate-600">Category</th>
                  <th className="pb-2 text-right text-xs font-semibold text-slate-600">Amount</th>
                </tr>
              </thead>
              <tbody>
                {incomeTransactions?.transactions.map((txn) => (
                  <tr key={txn.id} className="border-b border-slate-100">
                    <td className="py-2 text-xs text-slate-500">
                      {new Date(txn.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </td>
                    <td className="py-2 text-sm text-slate-900">{txn.description}</td>
                    <td className="py-2 text-xs text-slate-500">{txn.category}</td>
                    <td className="py-2 text-right text-sm font-semibold text-green-600">
                      {formatMoney(txn.amount)}
                    </td>
                  </tr>
                ))}
                <tr className="border-t-2 border-slate-300">
                  <td colSpan={3} className="py-2 text-sm font-semibold text-slate-900">
                    Total
                  </td>
                  <td className="py-2 text-right text-sm font-bold text-green-600">
                    {formatMoney(incomeTransactions?.total ?? 0)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        {/* Expense Transactions */}
        <article className="glass-panel p-5">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Current Month Expenses</h2>
            <p className="text-sm text-slate-500">{expenseTransactions?.count ?? 0} transactions</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="pb-2 text-left text-xs font-semibold text-slate-600">Date</th>
                  <th className="pb-2 text-left text-xs font-semibold text-slate-600">Description</th>
                  <th className="pb-2 text-left text-xs font-semibold text-slate-600">Category</th>
                  <th className="pb-2 text-right text-xs font-semibold text-slate-600">Amount</th>
                </tr>
              </thead>
              <tbody>
                {expenseTransactions?.transactions.map((txn) => (
                  <tr key={txn.id} className="border-b border-slate-100">
                    <td className="py-2 text-xs text-slate-500">
                      {new Date(txn.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </td>
                    <td className="py-2 text-sm text-slate-900">{txn.description}</td>
                    <td className="py-2 text-xs text-slate-500">{txn.category}</td>
                    <td className="py-2 text-right text-sm font-semibold text-red-600">
                      {formatMoney(txn.amount)}
                    </td>
                  </tr>
                ))}
                <tr className="border-t-2 border-slate-300">
                  <td colSpan={3} className="py-2 text-sm font-semibold text-slate-900">
                    Total
                  </td>
                  <td className="py-2 text-right text-sm font-bold text-red-600">
                    {formatMoney(expenseTransactions?.total ?? 0)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </div>

      {/* Historical Time Series Chart */}
      <article className="glass-panel p-5">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">12-Month Trend</h2>
            <p className="text-sm text-slate-500">Historical income and expense comparison</p>
          </div>
          <div className="flex gap-4 text-sm">
            <div>
              <span className="text-slate-500">Avg Income: </span>
              <span className="font-semibold text-green-600">{formatMoney(avgMonthlyIncome)}</span>
            </div>
            <div>
              <span className="text-slate-500">Avg Expense: </span>
              <span className="font-semibold text-red-600">{formatMoney(avgMonthlyExpense)}</span>
            </div>
          </div>
        </div>

        <div className="h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={combinedTimeSeries} margin={{ left: 20, right: 20, top: 10, bottom: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: '#64748b', fontSize: 11 }} 
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
              <Tooltip 
                formatter={(value) => formatMoney(Number(value))}
                contentStyle={{ backgroundColor: 'white', border: '1px solid #e2e8f0', borderRadius: '8px' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="income" 
                stroke="#10b981" 
                strokeWidth={2} 
                name="Income"
                dot={{ fill: '#10b981', r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="expense" 
                stroke="#ef4444" 
                strokeWidth={2} 
                name="Expenses"
                dot={{ fill: '#ef4444', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </article>
    </section>
  )
}

export default AccountingPage
