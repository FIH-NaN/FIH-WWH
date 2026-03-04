import './App.css'

type AssetItem = {
  name: string
  category: 'Bank Deposit' | 'Digital Asset' | 'Stock' | 'ETF' | 'Bond' | 'Real Estate'
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

const assets: AssetItem[] = [
  { name: 'Citi Savings', category: 'Bank Deposit', value: 52000, currency: 'USD', liquid: true },
  { name: 'BTC Wallet', category: 'Digital Asset', value: 14800, currency: 'USD', liquid: true },
  { name: 'AAPL', category: 'Stock', value: 26700, currency: 'USD', liquid: true },
  { name: 'VOO', category: 'ETF', value: 31600, currency: 'USD', liquid: true },
  { name: 'US Treasury 10Y', category: 'Bond', value: 9000, currency: 'USD', liquid: false },
  { name: 'Condo Unit', category: 'Real Estate', value: 280000, currency: 'USD', liquid: false },
]

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

function App() {
  const totalAssetValue = assets.reduce((sum, item) => sum + item.value, 0)
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

  return (
    <main className="page">
      <header className="header">
        <div>
          <h1>Wealth Dashboard</h1>
          <p>Unified snapshot of assets, liabilities, cash flows, income, and expenses.</p>
        </div>
        <span className="pill">As of 2026-03-04</span>
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
                <tr key={asset.name}>
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
                  <div className="bar-fill" style={{ width: `${(value / totalAssetValue) * 100}%` }} />
                </div>
                <span>{formatMoney(value)}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-head">
            <h3>Liabilities</h3>
            <span>{liabilities.length} obligations</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Category</th>
                <th className="align-right">Outstanding</th>
                <th className="align-right">Monthly Pay</th>
              </tr>
            </thead>
            <tbody>
              {liabilities.map((liability) => (
                <tr key={liability.name}>
                  <td>{liability.name}</td>
                  <td>{liability.category}</td>
                  <td className="align-right">{formatMoney(liability.outstanding, liability.currency)}</td>
                  <td className="align-right">{formatMoney(liability.monthlyPayment, liability.currency)}</td>
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

export default App
