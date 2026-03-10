import { apiRequest } from './api'
import type { ApiEnvelope, BudgetPayload, MonthlyTransactions, TimeSeries } from '../types/models'

export const accountingService = {
  async getCurrentMonthIncome(token: string): Promise<MonthlyTransactions> {
    const res = await apiRequest<ApiEnvelope<MonthlyTransactions>>('/accounting/current-month?flow=income', { token })
    return res.data
  },

  async getCurrentMonthExpense(token: string): Promise<MonthlyTransactions> {
    const res = await apiRequest<ApiEnvelope<MonthlyTransactions>>('/accounting/current-month?flow=expense', { token })
    return res.data
  },

  async getLastTwelveMonthsIncome(token: string): Promise<TimeSeries> {
    const res = await apiRequest<ApiEnvelope<TimeSeries>>('/accounting/series-12m?flow=income', { token })
    return res.data
  },

  async getLastTwelveMonthsExpense(token: string): Promise<TimeSeries> {
    const res = await apiRequest<ApiEnvelope<TimeSeries>>('/accounting/series-12m?flow=expense', { token })
    return res.data
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
