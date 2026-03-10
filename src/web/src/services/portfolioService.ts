import { apiRequest } from './api'
import type {
  AIAdvice,
  ApiEnvelope,
  InvestmentPortfolio,
  MarketData,
  Portfolio,
  WealthInsightsPayload,
} from '../types/models'

const toAdvice = (payload: WealthInsightsPayload): AIAdvice => ({
  advice: payload.recommendations?.length ? payload.recommendations.join(' ') : payload.insight_error ?? 'No advice available yet.',
})

export const portfolioService = {
  async getPortfolio(token: string): Promise<Portfolio> {
    const res = await apiRequest<ApiEnvelope<Portfolio>>('/portfolio/summary', { token })
    return res.data
  },

  async getInvestments(token: string): Promise<InvestmentPortfolio> {
    const res = await apiRequest<ApiEnvelope<InvestmentPortfolio>>('/portfolio/investment-holdings', { token })
    return {
      total_value_usd: res.data.total_value_usd ?? 0,
      holdings: (res.data.holdings ?? []).sort((a, b) => b.value_usd - a.value_usd),
    }
  },

  async getMarketData(token: string): Promise<MarketData> {
    const res = await apiRequest<ApiEnvelope<MarketData>>('/market/indicators', { token })
    return res.data
  },

  async getDefaultAdvice(token: string): Promise<AIAdvice> {
    const res = await apiRequest<ApiEnvelope<WealthInsightsPayload>>('/assets/wealth-overview/insights', { token })
    return toAdvice(res.data)
  },

  async getPromptBasedAdvice(token: string, prompt: string): Promise<AIAdvice> {
    const res = await apiRequest<ApiEnvelope<{ id: number; title: string; messages: Array<{ role: string; content: string }> }>>('/advisor/chat/messages', {
      method: 'POST',
      token,
      body: { message: prompt },
    })
    const messages = res.data.messages ?? []
    const latestAssistant = [...messages].reverse().find((msg) => msg.role === 'assistant')
    return { advice: latestAssistant?.content ?? 'No response from advisor.' }
  },
}
