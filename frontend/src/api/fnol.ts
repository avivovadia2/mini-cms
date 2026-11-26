import { apiClient } from './client'
import type { Page } from './page'
import type { PolicyInfo } from './policies'

// Mirror the backend schemas (app/modules/fnol/schemas). Change both sides together.

export type FnolStatus = 'submitted' | 'converted' | 'rejected'

export const FNOL_STATUS_LABELS: Record<FnolStatus, string> = {
  submitted: 'Submitted',
  converted: 'Converted',
  rejected: 'Rejected',
}

// FnolResponse on the server: the FNOL plus its matched policy (null when nothing matched).
export interface FnolInfo {
  id: number
  organization_id: number
  reported_policy_number: string // exactly what the reporter typed
  policy_id: number | null
  reporter_name: string
  reporter_email: string | null
  reporter_phone: string | null
  loss_date: string // "YYYY-MM-DD"
  loss_description: string
  loss_state: string | null
  status: FnolStatus
  rejection_reason: string | null
  submitted_by_id: number
  created_at: string
  policy: PolicyInfo | null
}

// Optional fields may be sent as '': the server stores a blank value as null.
export interface ReportLossRequest {
  reported_policy_number: string
  reporter_name: string
  reporter_email: string
  reporter_phone: string
  loss_date: string
  loss_description: string
  loss_state: string
}

export interface FnolListParams {
  page_number: number
  page_size: number
  status?: FnolStatus
}

export async function listFnols(params: FnolListParams): Promise<Page<FnolInfo>> {
  const response = await apiClient.get<Page<FnolInfo>>('/fnols', { params })
  return response.data
}

export async function getFnol(fnolId: number): Promise<FnolInfo> {
  const response = await apiClient.get<FnolInfo>(`/fnols/${fnolId}`)
  return response.data
}

export async function reportLoss(request: ReportLossRequest): Promise<FnolInfo> {
  const response = await apiClient.post<FnolInfo>('/fnols', request)
  return response.data
}

export async function rejectFnol(fnolId: number, rejectionReason: string): Promise<FnolInfo> {
  const response = await apiClient.post<FnolInfo>(`/fnols/${fnolId}/reject`, {
    rejection_reason: rejectionReason,
  })
  return response.data
}
