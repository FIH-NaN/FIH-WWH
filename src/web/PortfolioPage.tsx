import { Sparkles, TrendingUp, Send, Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import Plot from 'react-plotly.js'
import { formatMoney } from '../lib/format'
import { portfolioService } from '../services/portfolioService'
import type { Portfolio, InvestmentPortfolio, MarketData, AIAdvice } from '../services/portfolioService'
import { useAuth } from '../state/AuthContext'

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
          portfolioService.getMarketData(),
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
  }, [token])

  const handlePromptSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
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

  const assetColors = ['#14b8a6', '#2563eb', '#f59e0b', '#8b5cf6', '#10b981', '#ec4899', '#06b6d4', '#6366f1']
  const liabilityColors = ['#ef4444', '#f97316', '#f59e0b', '#eab308']

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
        {/* Assets Pie Chart */}
        <article className="glass-panel p-5">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Assets Allocation</h2>
            <p className="text-sm text-slate-500">Current asset distribution</p>
          </div>
          <div className="space-y-2">
            {portfolio?.assets.slice(0, 5).map((asset, idx) => (
              <div key={asset.name} className="flex justify-between text-sm">
                <span className="text-slate-700">{asset.name}</span>
                <span className="font-semibold">{formatMoney(asset.value)}</span>
              </div>
            ))}
          </div>
        </article>

        {/* Liabilities */}
        <article className="glass-panel p-5">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Liabilities</h2>
            <p className="text-sm text-slate-500">Current obligations</p>
          </div>
          <div className="space-y-2">
            {portfolio?.liabilities.map((liability, idx) => (
              <div key={liability.name} className="flex justify-between text-sm">
                <span className="text-slate-700">{liability.name}</span>
                <span className="font-semibold">{formatMoney(liability.amount)}</span>
              </div>
            ))}
          </div>
        </article>
      </div>

      {/* Market Data */}
      <article className="glass-panel p-5">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-slate-900">Market Indicators</h2>
        </div>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          {marketData?.indicators.map((indicator) => (
            <div key={indicator.name} className="rounded bg-slate-50 p-3">
              <div className="text-xs text-slate-500">{indicator.name}</div>
              <div className="mt-1 text-lg font-semibold">{indicator.value.toFixed(2)}{indicator.unit}</div>
            </div>
          ))}
        </div>
      </article>

      {/* AI Advice */}
      <article className="glass-panel p-5">
        <div className="inline-flex items-center gap-2 rounded-lg bg-slate-100 px-2 py-1 text-xs font-semibold">
          <Sparkles size={13} />
          AI Advisor
        </div>
        <div className="mt-4 space-y-3">
          {aiAdvice && <p className="rounded-xl bg-slate-50 p-3 text-sm">{aiAdvice.advice}</p>}
          <form onSubmit={handlePromptSubmit} className="flex gap-2">
            <input
              type="text"
              value={promptInput}
              onChange={(e) => setPromptInput(e.target.value)}
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
