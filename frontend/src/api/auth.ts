import { apiClient } from './client'

// These interfaces mirror the backend's Pydantic schemas (app/modules/auth/schemas,
// app/modules/organizations/schemas). Change both sides together.

export interface OrganizationInfo {
  id: number
  name: string
}

export interface MeResponse {
  id: number
  email: string
  full_name: string
  organization: OrganizationInfo
}

export interface RegisterRequest {
  organization_name: string
  full_name: string
  email: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
}

export async function register(request: RegisterRequest): Promise<MeResponse> {
  const response = await apiClient.post<MeResponse>('/auth/register', request)
  return response.data
}

export async function login(request: LoginRequest): Promise<MeResponse> {
  const response = await apiClient.post<MeResponse>('/auth/login', request)
  return response.data
}

export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout')
}

export async function getMe(): Promise<MeResponse> {
  const response = await apiClient.get<MeResponse>('/auth/me')
  return response.data
}
