import { Sparkles, TrendingUp, Send, Loader2 } from 'lucide-react'
import { useEffect, useState, type FormEvent } from 'react'
import { Cell, Pie, PieChart, ResponsiveContainer } from 'recharts'
import { formatMoney } from '../lib/format'
import { portfolioService } from '../services/portfolioService'
import type { AIAdvice, InvestmentPortfolio, MarketData, Portfolio } from '../types/models'
import { useAuth } from '../state/AuthContext'

const HOLDING_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1']

function PortfolioPage() {
  const { token } = useAuth()
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [investments, setInvestments] = useState<InvestmentPortfolio | null>(null)
  const [marketData, setMarketData] = useState<MarketData | null>(null)
  const [aiAdvice, setAiAdvice] = useState<AIAdvice | null>(null)
  const [loading, setLoading] = useState(true)
  const [promptInput, setPromptInput] = useState('')
  const [submittingPrompt, setSubmittingPrompt] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      if (!token) return
      setLoading(true)
      try {
        const [portfolioData, investmentData, market, advice] = await Promise.all([
          portfolioService.getPortfolio(token),
          portfolioService.getInvestments(token),
          portfolioService.getMarketData(token),
          portfolioService.getDefaultAdvice(token),
        ])
        setPortfolio(portfolioData)
        setInvestments(investmentData)
        setMarketData(market)
        setAiAdvice(advice)
      } catch (error) {
        console.error('Error fetching portfolio data:', error)
      } finally {
        setLoading(false)
      }
    }

    void fetchData()

    const refresh = () => {
      void fetchData()
    }
    window.addEventListener('wwh:assets-updated', refresh)
    return () => window.removeEventListener('wwh:assets-updated', refresh)
  }, [token])

  const handlePromptSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!token || !promptInput.trim()) return

    setSubmittingPrompt(true)
    try {
      const advice = await portfolioService.getPromptBasedAdvice(token, promptInput.trim())
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
        <div className="text-slate-500">Loading portfolio...</div>
      </div>
    )
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-slate-900">Portfolio Analysis</h1>
          <p className="mt-1 text-sm text-slate-500">Detailed breakdown of assets, liabilities, and market insights</p>
        </div>
        <div className="inline-flex items-center gap-1 rounded-lg bg-green-50 px-3 py-2 text-sm font-semibold text-green-700">
          <TrendingUp size={16} />
          Net Worth: {formatMoney(portfolio?.net_worth ?? 0)}
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <article className="glass-panel p-5">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Assets Allocation</h2>
            <p className="text-sm text-slate-500">Current asset distribution</p>
          </div>
          <div className="space-y-2">
            {(portfolio?.assets ?? []).slice(0, 5).map((asset) => (
              <div key={asset.name} className="flex justify-between text-sm">
                <span className="text-slate-700">{asset.name}</span>
                <span className="font-semibold">{formatMoney(asset.value)}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="glass-panel p-5">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Liabilities</h2>
            <p className="text-sm text-slate-500">Current obligations</p>
          </div>
          <div className="space-y-2">
            {(portfolio?.liabilities ?? []).length ? (
              portfolio?.liabilities.map((liability) => (
                <div key={liability.name} className="flex justify-between text-sm">
                  <span className="text-slate-700">{liability.name}</span>
                  <span className="font-semibold">{formatMoney(liability.amount)}</span>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500">No liabilities data available.</p>
            )}
          </div>
        </article>
      </div>

      <article className="glass-panel p-5">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-slate-900">Investment Holdings</h2>
          <p className="text-sm text-slate-500">Detailed distribution by synced investment positions</p>
        </div>
        <div className="grid gap-4 lg:grid-cols-[260px,1fr]">
          <div className="h-64">
            {(investments?.holdings ?? []).length ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={investments?.holdings ?? []}
                    dataKey="value_usd"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={72}
                    outerRadius={102}
                    paddingAngle={2}
                    stroke="#ffffff"
                    strokeWidth={2}
                  >
                    {(investments?.holdings ?? []).map((item, index) => (
                      <Cell key={`${item.name}-${item.symbol ?? 'na'}-${index}`} fill={HOLDING_COLORS[index % HOLDING_COLORS.length]} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-slate-500">No investment holdings yet.</div>
            )}
          </div>

          <div className="space-y-2">
            {(investments?.holdings ?? []).map((item, index) => (
              <div key={`${item.name}-${item.symbol ?? 'na'}-${index}`} className="flex items-start justify-between gap-3 rounded-lg border border-slate-100 px-3 py-2 text-sm">
                <div className="min-w-0">
                  <div className="flex items-start gap-2">
                    <span
                      className="mt-1 inline-block h-2.5 w-2.5 flex-none rounded-full"
                      style={{ backgroundColor: HOLDING_COLORS[index % HOLDING_COLORS.length] }}
                    />
                    <div className="min-w-0">
                      <p className="truncate font-medium text-slate-800">{item.name}</p>
                      <p className="truncate text-xs text-slate-500">
                        {item.symbol ? `${item.symbol}` : 'N/A'}
                        {item.account_name ? ` · ${item.account_name}` : ''}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-slate-900">{formatMoney(item.value_usd)}</p>
                  <p className="text-xs text-slate-500">{item.weight_pct.toFixed(2)}%</p>
                </div>
              </div>
            ))}
            {(investments?.holdings ?? []).length ? (
              <div className="pt-2 text-right text-sm font-semibold text-slate-700">Total: {formatMoney(investments?.total_value_usd ?? 0)}</div>
            ) : null}
          </div>
        </div>
      </article>

      <article className="glass-panel p-5">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-slate-900">Market Indicators</h2>
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          {(marketData?.groups ?? []).length ? (
            marketData?.groups.map((group) => (
              <div key={group.group} className="rounded-xl border border-slate-100 bg-slate-50 p-3">
                <h3 className="text-sm font-semibold capitalize text-slate-800">{group.group.replace('_', ' ')}</h3>
                <div className="mt-3 space-y-2">
                  {group.indicators.map((indicator) => (
                    <div key={`${group.group}-${indicator.symbol}`} className="flex items-center justify-between rounded-lg bg-white px-3 py-2">
                      <span className="text-xs text-slate-600">{indicator.symbol}</span>
                      <span className="text-sm font-semibold text-slate-900">
                        {indicator.value.toFixed(2)}
                        {indicator.unit}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-500">Market indicators will appear when market-data API is available.</p>
          )}
        </div>
      </article>

      <article className="glass-panel p-5">
        <div className="inline-flex items-center gap-2 rounded-lg bg-slate-100 px-2 py-1 text-xs font-semibold">
          <Sparkles size={13} />
          AI Advisor
        </div>
        <div className="mt-4 space-y-3">
          {aiAdvice ? <p className="rounded-xl bg-slate-50 p-3 text-sm">{aiAdvice.advice}</p> : null}
          <form onSubmit={handlePromptSubmit} className="flex gap-2">
            <input
              type="text"
              value={promptInput}
              onChange={(event) => setPromptInput(event.target.value)}
              placeholder="Ask about your portfolio..."
              className="flex-1 rounded-lg border px-3 py-2 text-sm"
              disabled={submittingPrompt}
            />
            <button
              type="submit"
              disabled={submittingPrompt || !promptInput.trim()}
              className="rounded-lg bg-teal-600 px-3 py-2 text-white"
            >
              {submittingPrompt ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
            </button>
          </form>
        </div>
      </article>
    </section>
  )
}

export default PortfolioPage
