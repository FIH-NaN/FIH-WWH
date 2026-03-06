import { TrendingUp } from 'lucide-react'
import Plot from 'react-plotly.js'
import { formatMoney } from '../lib/format'

// Mock data for portfolio composition
const portfolioComposition = [
  { name: 'Stocks', value: 45000, percentage: 35, color: '#14b8a6' },
  { name: 'Bonds', value: 32000, percentage: 25, color: '#2563eb' },
  { name: 'Crypto', value: 26000, percentage: 20, color: '#f59e0b' },
  { name: 'Real Estate', value: 19000, percentage: 15, color: '#8b5cf6' },
  { name: 'Cash', value: 6500, percentage: 5, color: '#64748b' },
]

// Mock data for 12-month profit/loss
const profitLossData = [
  { month: 'Jan', value: 2400 },
  { month: 'Feb', value: -800 },
  { month: 'Mar', value: 3200 },
  { month: 'Apr', value: 1600 },
  { month: 'May', value: 4800 },
  { month: 'Jun', value: 2100 },
  { month: 'Jul', value: -1200 },
  { month: 'Aug', value: 3800 },
  { month: 'Sep', value: 2900 },
  { month: 'Oct', value: 5200 },
  { month: 'Nov', value: 1800 },
  { month: 'Dec', value: 4100 },
]

// Mock data for efficient frontier
// Points on the efficient frontier curve
const efficientFrontierData = [
  { risk: 5, return: 3 },
  { risk: 8, return: 5 },
  { risk: 10, return: 6.5 },
  { risk: 12, return: 7.8 },
  { risk: 15, return: 9 },
  { risk: 18, return: 10 },
  { risk: 20, return: 10.8 },
  { risk: 23, return: 11.5 },
  { risk: 25, return: 12 },
  { risk: 28, return: 12.3 },
  { risk: 30, return: 12.5 },
]

// User's current portfolio position
const userPosition = { risk: 17, return: 8.5, name: 'Your Portfolio' }

// Sub-optimal portfolios (below the efficient frontier)
const subOptimalPoints = [
  { risk: 12, return: 5 },
  { risk: 15, return: 6 },
  { risk: 20, return: 7 },
  { risk: 25, return: 9 },
]

function PortfolioPage() {
  const totalValue = portfolioComposition.reduce((sum, item) => sum + item.value, 0)
  const totalProfitLoss = profitLossData.reduce((sum, item) => sum + item.value, 0)
  const avgMonthlyReturn = (totalProfitLoss / profitLossData.length).toFixed(0)

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-slate-900">Portfolio Analysis</h1>
          <p className="mt-1 text-sm text-slate-500">Composition, performance, and optimization insights</p>
        </div>
        <div className="inline-flex items-center gap-1 rounded-lg bg-green-50 px-3 py-2 text-sm font-semibold text-green-700">
          <TrendingUp size={16} />
          {totalProfitLoss > 0 ? '+' : ''}
          {formatMoney(totalProfitLoss)} YTD
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        {/* Portfolio Composition - Interactive Pie Chart */}
        <article className="glass-panel p-5">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Portfolio Composition</h2>
            <p className="text-sm text-slate-500">Current asset allocation by category</p>
          </div>

          <div className="flex flex-col items-center gap-4">
            <Plot
              data={[
                {
                  type: 'pie',
                  labels: portfolioComposition.map((item) => item.name),
                  values: portfolioComposition.map((item) => item.value),
                  marker: {
                    colors: portfolioComposition.map((item) => item.color),
                  },
                  textinfo: 'label+percent',
                  textposition: 'outside',
                  automargin: true,
                  hovertemplate: '<b>%{label}</b><br>Value: $%{value:,.0f}<br>%{percent}<extra></extra>',
                  hole: 0.35,
                },
              ]}
              layout={{
                height: 380,
                margin: { t: 20, b: 20, l: 20, r: 20 },
                showlegend: false,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: { family: 'inherit', size: 12, color: '#475569' },
                annotations: [
                  {
                    text: `<b>${formatMoney(totalValue)}</b><br><span style="font-size:11px;color:#64748b">Total Value</span>`,
                    showarrow: false,
                    font: { size: 16, color: '#0f172a' },
                  },
                ],
              }}
              config={{
                responsive: true,
                displayModeBar: false,
              }}
              className="w-full"
            />

            <div className="w-full space-y-1.5">
              {portfolioComposition.map((item) => (
                <div key={item.name} className="flex items-center justify-between gap-3 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-sm" style={{ backgroundColor: item.color }} />
                    <span className="text-slate-700">{item.name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-slate-900">{formatMoney(item.value)}</span>
                    <span className="w-10 text-right text-slate-500">{item.percentage}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </article>

        {/* 12-Month Profit/Loss - Interactive Area Chart */}
        <article className="glass-panel p-5">
          <div className="mb-4 flex items-start justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">12-Month Performance</h2>
              <p className="text-sm text-slate-500">Monthly profit and loss trend</p>
            </div>
            <div className="text-right">
              <p className="text-xs uppercase tracking-wider text-slate-500">Avg Monthly</p>
              <p className="font-display text-xl font-semibold text-slate-900">
                {Number(avgMonthlyReturn) > 0 ? '+' : ''}
                {formatMoney(Number(avgMonthlyReturn))}
              </p>
            </div>
          </div>

          <Plot
            data={[
              {
                x: profitLossData.map((d) => d.month),
                y: profitLossData.map((d) => d.value),
                type: 'scatter',
                mode: 'lines',
                fill: 'tozeroy',
                line: { color: '#059669', width: 2, shape: 'spline' },
                fillcolor: 'rgba(16, 185, 129, 0.2)',
                hovertemplate: '<b>%{x}</b><br>P&L: $%{y:,.0f}<extra></extra>',
              },
            ]}
            layout={{
              height: 300,
              margin: { t: 10, b: 40, l: 60, r: 20 },
              xaxis: {
                showgrid: false,
                zeroline: false,
                color: '#64748b',
              },
              yaxis: {
                showgrid: true,
                gridcolor: '#e2e8f0',
                zeroline: true,
                zerolinecolor: '#cbd5e1',
                zerolinewidth: 1,
                color: '#64748b',
                tickformat: '$,.0f',
              },
              paper_bgcolor: 'rgba(0,0,0,0)',
              plot_bgcolor: 'rgba(0,0,0,0)',
              font: { family: 'inherit', size: 11, color: '#475569' },
              hovermode: 'x unified',
            }}
            config={{
              responsive: true,
              displayModeBar: false,
            }}
            className="w-full"
          />
        </article>
      </div>

      {/* Efficient Frontier - Interactive Scatter Plot */}
      <article className="glass-panel p-5">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-slate-900">Efficient Frontier Analysis</h2>
          <p className="text-sm text-slate-500">
            Risk-return trade-off and portfolio optimization opportunities
          </p>
        </div>

        <Plot
          data={[
            // Sub-optimal portfolios
            {
              x: subOptimalPoints.map((d) => d.risk),
              y: subOptimalPoints.map((d) => d.return),
              type: 'scatter',
              mode: 'markers',
              name: 'Sub-optimal',
              marker: {
                size: 10,
                color: '#94a3b8',
                opacity: 0.5,
                line: { color: '#64748b', width: 1 },
              },
              hovertemplate: '<b>Sub-optimal Portfolio</b><br>Risk: %{x}%<br>Return: %{y}%<extra></extra>',
            },
            // Efficient Frontier curve
            {
              x: efficientFrontierData.map((d) => d.risk),
              y: efficientFrontierData.map((d) => d.return),
              type: 'scatter',
              mode: 'lines+markers',
              name: 'Efficient Frontier',
              line: { color: '#14b8a6', width: 3, shape: 'spline' },
              marker: { size: 8, color: '#14b8a6' },
              hovertemplate: '<b>Efficient Portfolio</b><br>Risk: %{x}%<br>Return: %{y}%<extra></extra>',
            },
            // User's current position
            {
              x: [userPosition.risk],
              y: [userPosition.return],
              type: 'scatter',
              mode: 'markers',
              name: 'Your Portfolio',
              marker: {
                size: 20,
                color: '#f59e0b',
                symbol: 'star',
                line: { color: '#d97706', width: 2 },
              },
              hovertemplate: `<b>Your Portfolio</b><br>Risk: ${userPosition.risk}%<br>Return: ${userPosition.return}%<extra></extra>`,
            },
          ]}
          layout={{
            height: 450,
            margin: { t: 20, b: 60, l: 60, r: 20 },
            xaxis: {
              title: {
                text: 'Risk (Volatility %)',
                font: { size: 13, color: '#475569' },
              },
              showgrid: true,
              gridcolor: '#e2e8f0',
              color: '#64748b',
              range: [0, 35],
            },
            yaxis: {
              title: {
                text: 'Expected Return (%)',
                font: { size: 13, color: '#475569' },
              },
              showgrid: true,
              gridcolor: '#e2e8f0',
              color: '#64748b',
              range: [0, 15],
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(255,255,255,0.5)',
            font: { family: 'inherit', size: 12, color: '#475569' },
            hovermode: 'closest',
            legend: {
              x: 0.02,
              y: 0.98,
              bgcolor: 'rgba(255,255,255,0.9)',
              bordercolor: '#e2e8f0',
              borderwidth: 1,
              font: { size: 11 },
            },
            shapes: [
              {
                type: 'rect',
                xref: 'paper',
                yref: 'paper',
                x0: 0,
                y0: 0,
                x1: 1,
                y1: 1,
                line: {
                  color: '#e2e8f0',
                  width: 1,
                },
                fillcolor: 'rgba(0,0,0,0)',
              },
            ],
          }}
          config={{
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            displaylogo: false,
          }}
          className="w-full"
        />

        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <div className="rounded-xl bg-slate-50 p-3 text-sm">
            <div className="mb-1 flex items-center gap-2">
              <div className="h-2.5 w-2.5 rounded-full bg-[#14b8a6]" />
              <span className="font-semibold text-slate-700">Efficient Frontier</span>
            </div>
            <p className="text-xs text-slate-600">Optimal risk-return combinations</p>
          </div>
          <div className="rounded-xl bg-slate-50 p-3 text-sm">
            <div className="mb-1 flex items-center gap-2">
              <div className="h-2.5 w-2.5 rounded-full bg-[#f59e0b]" />
              <span className="font-semibold text-slate-700">Your Position</span>
            </div>
            <p className="text-xs text-slate-600">
              Current: {userPosition.risk}% risk, {userPosition.return}% return
            </p>
          </div>
          <div className="rounded-xl bg-slate-50 p-3 text-sm">
            <div className="mb-1 flex items-center gap-2">
              <div className="h-2.5 w-2.5 rounded-full bg-[#94a3b8]" />
              <span className="font-semibold text-slate-700">Sub-optimal</span>
            </div>
            <p className="text-xs text-slate-600">Below-frontier portfolios</p>
          </div>
        </div>

        <div className="mt-4 rounded-xl border border-teal-200 bg-teal-50 p-4">
          <p className="text-sm font-semibold text-teal-900">💡 Optimization Insight</p>
          <p className="mt-1 text-sm text-teal-800">
            Your portfolio is currently below the efficient frontier. Consider rebalancing to achieve a better
            risk-return profile. You could potentially achieve a 10% return with similar risk, or maintain your 8.5%
            return with only 12% risk.
          </p>
        </div>
      </article>
    </section>
  )
}

export default PortfolioPage
