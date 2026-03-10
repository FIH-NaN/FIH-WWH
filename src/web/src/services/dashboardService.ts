import { apiRequest } from './api'
import type { AIAdvice, ApiEnvelope, BalanceSheet, BudgetPayload, IncomeStatement, WealthInsightsPayload } from '../types/models'

const toAdvice = (payload: WealthInsightsPayload): AIAdvice => ({
  advice: payload.recommendations?.length ? payload.recommendations.join(' ') : payload.insight_error ?? 'No advice available yet.',
})

export const dashboardService = {
  async getBalanceSheet(token: string): Promise<BalanceSheet> {
    const res = await apiRequest<ApiEnvelope<BalanceSheet>>('/dashboard/balance-sheet', { token })
    return res.data
  },

  async getIncomeStatement(token: string): Promise<IncomeStatement> {
    const res = await apiRequest<ApiEnvelope<IncomeStatement>>('/dashboard/income-statement', { token })
    return res.data
  },

  async getTotalIncome(token: string): Promise<number> {
    const res = await apiRequest<ApiEnvelope<{ total_income: number }>>('/dashboard/totals', { token })
    return Number(res.data.total_income ?? 0)
  },

  async getTotalExpense(token: string): Promise<number> {
    const res = await apiRequest<ApiEnvelope<{ total_expense: number }>>('/dashboard/totals', { token })
    return Number(res.data.total_expense ?? 0)
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

  async getBudgets(token: string, monthKey?: string): Promise<BudgetPayload> {
    const path = monthKey ? `/dashboard/budgets?month_key=${encodeURIComponent(monthKey)}` : '/dashboard/budgets'
    const res = await apiRequest<ApiEnvelope<BudgetPayload>>(path, { token })
    return res.data
  },

  async saveBudgets(
    token: string,
    monthKey: string,
    items: Array<{ flow_type: 'income' | 'expense'; category: string; amount: number }>,
  ): Promise<BudgetPayload> {
    const res = await apiRequest<ApiEnvelope<BudgetPayload>>('/dashboard/budgets', {
      method: 'PUT',
      token,
      body: { month_key: monthKey, items },
    })
    return res.data
  },
}
