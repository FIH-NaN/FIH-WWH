import { apiRequest } from './api'
import type { ApiEnvelope, LoginPayload, RegisterPayload, User } from '../types/models'

export async function login(email: string, password: string) {
  return apiRequest<ApiEnvelope<LoginPayload>>('/auth/login', {
    method: 'POST',
    body: { email, password },
  })
}

export async function register(name: string, email: string, password: string) {
  return apiRequest<ApiEnvelope<RegisterPayload>>('/auth/register', {
    method: 'POST',
    body: { name, email, password },
  })
}

export async function me(token: string) {
  return apiRequest<ApiEnvelope<User>>('/auth/me', { token })
}
