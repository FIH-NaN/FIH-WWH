import { AlertCircle, RefreshCw, Sparkles } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useEffect, useMemo, useState } from 'react'
import { formatMoney } from '../lib/format'
import { getWealthInsights, getWealthOverview, refreshWealthInsights } from '../services/assetsService'
import { useAuth } from '../state/AuthContext'
import type { WealthInsightsPayload, WealthOverviewPayload } from '../types/models'

function displayBucket(bucket: string): string {
  if (bucket === 'stocks') return 'Stocks'
  if (bucket === 'bonds') return 'Bonds'
  if (bucket === 'crypto') return 'Crypto'
  if (bucket === 'real_estate') return 'Real Estate'
  if (bucket === 'cash') return 'Cash'
  return 'Other'
}

function DashboardPage() {
  const { token } = useAuth()
  const [overview, setOverview] = useState<WealthOverviewPayload | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [insights, setInsights] = useState<WealthInsightsPayload | null>(null)
  const [insightsLoading, setInsightsLoading] = useState(false)
  const [insightsError, setInsightsError] = useState('')

  const formatGeneratedAt = (value?: string | null): string => {
    if (!value) return 'Not generated yet'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return value
    return date.toLocaleString()
  }

  useEffect(() => {
    const load = async () => {
      if (!token) return
      setLoading(true)
      setError('')
      try {
        const response = await getWealthOverview(token)
        setOverview(response.data)
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : 'Failed to load dashboard metrics')
      } finally {
        setLoading(false)
      }
    }

    const refresh = () => {
      void load()
      void loadInsights()
    }

    const loadInsights = async () => {
      if (!token) return
      setInsightsLoading(true)
      setInsightsError('')
      try {
        const response = await getWealthInsights(token)
        setInsights(response.data)
        if (response.data.insight_status !== 'success') {
          const errorMessage = response.data.insight_error || 'AI insights unavailable'
          setInsightsError(errorMessage)
        }
      } catch (requestError) {
        const message = requestError instanceof Error ? requestError.message : 'AI insights request failed'
        setInsightsError(message)
        setInsights(null)
      } finally {
        setInsightsLoading(false)
      }
    }

    void load()
    void loadInsights()
    window.addEventListener('wwh:assets-updated', refresh)
    return () => window.removeEventListener('wwh:assets-updated', refresh)
  }, [token])

  const handleRefreshInsights = async () => {
    if (!token) return
    setInsightsLoading(true)
    setInsightsError('')
    try {
      const response = await refreshWealthInsights(token)
      setInsights(response.data)
      if (response.data.insight_status !== 'success') {
        setInsightsError(response.data.insight_error ?? 'AI insights refresh failed')
      }
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'AI insights refresh failed'
      setInsightsError(message)
    } finally {
      setInsightsLoading(false)
    }
  }

  const allocationSeries = useMemo(
    () =>
      (overview?.allocation ?? [])
        .filter((item) => item.weight_pct > 0)
        .map((item) => ({
          bucket: displayBucket(item.bucket),
          weight: Number(item.weight_pct.toFixed(2)),
        })),
    [overview],
  )

  const cryptoShare = overview?.allocation.find((item) => item.bucket === 'crypto')?.weight_pct ?? 0
  const freshness = overview?.factors.find((factor) => factor.name === 'Data Freshness')?.score ?? 0
  const kpis = [
    { label: 'Total Assets', value: overview ? formatMoney(overview.total_portfolio_usd) : '--' },
    { label: 'Crypto Allocation', value: `${cryptoShare.toFixed(1)}%` },
    { label: 'Health Score', value: overview ? `${overview.overall_score} / 100` : '--' },
    { label: 'Freshness', value: `${freshness} / 100` },
  ]

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

      {error ? (
        <p className="inline-flex items-center gap-2 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
          <AlertCircle size={14} /> {error}
        </p>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[2fr_1fr]">
        <article className="glass-panel p-4">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Allocation Mix</h2>
              <p className="text-sm text-slate-500">Live portfolio composition by bucket</p>
            </div>
            <div className="inline-flex items-center gap-1 rounded-lg bg-teal-50 px-2 py-1 text-xs font-semibold text-teal-700">
              Grade {overview?.grade ?? '--'}
            </div>
          </div>

          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={allocationSeries} margin={{ left: 8, right: 8, top: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="bucket" tick={{ fill: '#64748b', fontSize: 12 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 12 }} unit="%" />
                <Tooltip formatter={(value) => `${Number(value).toFixed(2)}%`} />
                <Bar dataKey="weight" fill="#0f766e" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          {loading ? <p className="mt-2 text-xs text-slate-500">Loading live metrics...</p> : null}
        </article>

        <article className="rounded-2xl border border-transparent bg-white p-4 shadow-panel [background:linear-gradient(white,white)_padding-box,linear-gradient(135deg,#14b8a6,#2563eb)_border-box]">
          <div className="flex items-center justify-between">
            <div className="inline-flex items-center gap-2 rounded-lg bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
              <Sparkles size={13} />
              AI Insights
            </div>
            <button
              type="button"
              onClick={() => handleRefreshInsights()}
              disabled={insightsLoading}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs text-slate-600 disabled:opacity-60"
            >
              <RefreshCw size={12} className={insightsLoading ? 'animate-spin' : ''} />
              Refresh
            </button>
          </div>
          <p className="mt-2 text-xs text-slate-500">Source: {insights?.insight_source === 'cached' ? `Cached ${insights.insight_provider}` : insights?.insight_source === 'ai' ? `Live ${insights.insight_provider}` : 'No insights yet'}</p>
          <p className="mt-1 text-xs text-slate-500">Generated: {formatGeneratedAt(insights?.generated_at)}</p>
          {insightsError ? <p className="mt-1 rounded-lg bg-amber-50 px-2 py-1 text-xs text-amber-700">Reason: {insightsError}</p> : null}
          <h3 className="mt-3 font-display text-lg text-slate-900">Actionable Recommendations</h3>

          <div className="mt-4 space-y-3 text-sm text-slate-600">
            {insightsLoading ? <p className="rounded-xl bg-slate-50 p-3">AI insights loading...</p> : null}
            {(insights?.recommendations ?? []).slice(0, 3).map((tip) => (
              <p key={tip} className="rounded-xl bg-slate-50 p-3">
                {tip}
              </p>
            ))}
            {!insightsLoading && !insightsError && !(insights?.recommendations?.length ?? 0) ? (
              <p className="rounded-xl bg-slate-50 p-3">No AI insights returned.</p>
            ) : null}
          </div>
        </article>
      </div>
    </section>
  )
}

export default DashboardPage
