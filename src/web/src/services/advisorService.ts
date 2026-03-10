import { apiRequest } from './api'
import type { AdvisorConversation, AdvisorConversationSummary, ApiEnvelope } from '../types/models'

export const advisorService = {
  async listConversations(token: string): Promise<AdvisorConversationSummary[]> {
    const res = await apiRequest<ApiEnvelope<{ items: AdvisorConversationSummary[] }>>('/advisor/chat/conversations', { token })
    return res.data.items ?? []
  },

  async getConversation(token: string, conversationId: number): Promise<AdvisorConversation> {
    const res = await apiRequest<ApiEnvelope<AdvisorConversation>>(`/advisor/chat/conversations/${conversationId}`, { token })
    return res.data
  },

  async sendMessage(token: string, message: string, conversationId?: number): Promise<AdvisorConversation> {
    const res = await apiRequest<ApiEnvelope<AdvisorConversation>>('/advisor/chat/messages', {
      method: 'POST',
      token,
      body: {
        message,
        conversation_id: conversationId,
      },
    })
    return res.data
  },
}
