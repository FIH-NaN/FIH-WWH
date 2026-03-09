import { RefreshCw } from 'lucide-react'
import { useEffect, useState } from 'react'
import { getWealthInsights, getWealthOverview, refreshWealthInsights } from '../services/assetsService'
import { useAuth } from '../state/AuthContext'
import type { WealthInsightsPayload, WealthOverviewPayload } from '../types/models'

function AdvisorPage() {
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
        setError(requestError instanceof Error ? requestError.message : 'Failed to load advisor data')
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
          setInsightsError(response.data.insight_error || 'AI insights unavailable')
        }
      } catch (requestError) {
        setInsightsError(requestError instanceof Error ? requestError.message : 'Failed to load AI insights')
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
        setInsightsError(response.data.insight_error || 'AI insights refresh failed')
      }
    } catch (requestError) {
      setInsightsError(requestError instanceof Error ? requestError.message : 'AI insights refresh failed')
    } finally {
      setInsightsLoading(false)
    }
  }

  return (
    <section className="space-y-4">
      <article className="glass-panel p-6">
        <p className="text-xs uppercase tracking-[0.2em] text-teal-600">AI Advisor</p>
        <h1 className="mt-2 font-display text-2xl text-slate-900">Portfolio Diagnostics</h1>
        <p className="mt-2 text-sm text-slate-600">
          Deterministic metrics are used as guardrails for recommendation quality and explainability.
        </p>
        <div className="mt-2 flex items-center justify-between gap-2">
          <p className="text-xs text-slate-500">
            Source: {insights?.insight_source === 'cached' ? `Cached ${insights.insight_provider}` : insights?.insight_source === 'ai' ? `Live ${insights.insight_provider}` : 'No insights yet'}
          </p>
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
        <p className="mt-1 text-xs text-slate-500">Generated: {formatGeneratedAt(insights?.generated_at)}</p>
        {insightsError ? (
          <p className="mt-2 rounded-xl bg-amber-50 px-3 py-2 text-xs text-amber-700">Reason: {insightsError}</p>
        ) : null}
        {loading ? <p className="mt-3 text-sm text-slate-500">Loading advisor context...</p> : null}
        {error ? <p className="mt-3 rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p> : null}
      </article>

      <article className="glass-panel p-6">
        <div className="mb-3 flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-900">Factor Breakdown</p>
          <p className="text-xs text-slate-500">Score {overview?.overall_score ?? '--'} / 100</p>
        </div>

        {overview?.factors?.length ? (
          <div className="space-y-3">
            {overview.factors.map((factor) => (
              <div key={factor.name} className="rounded-xl border border-slate-200 bg-white p-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-slate-900">{factor.name}</p>
                  <p className="text-sm font-medium text-slate-700">
                    {factor.score}/100 (w {Math.round(factor.weight * 100)}%)
                  </p>
                </div>
                <p className="mt-1 text-xs text-slate-500">{factor.detail}</p>
              </div>
            ))}
          </div>
        ) : !loading ? (
          <p className="text-sm text-slate-500">No factor data available yet. Connect accounts and run sync.</p>
        ) : null}
      </article>

      <article className="glass-panel p-6">
        <p className="text-sm font-semibold text-slate-900">Current Recommendations</p>
        <div className="mt-3 space-y-2">
          {insightsLoading ? <p className="rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-600">AI insights loading...</p> : null}
          {(insights?.recommendations ?? []).map((recommendation) => (
            <p key={recommendation} className="rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-700">
              {recommendation}
            </p>
          ))}
          {!insightsLoading && !insightsError && !(insights?.recommendations?.length ?? 0) ? (
            <p className="rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-600">No recommendations yet.</p>
          ) : null}
        </div>
      </article>
    </section>
  )
}

export default AdvisorPage
