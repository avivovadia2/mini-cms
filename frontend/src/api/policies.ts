import { apiClient } from './client'
import type { Page } from './page'

// Mirror the backend schemas (app/modules/policies/schemas). Change both sides together.

export type LineOfBusiness = 'auto' | 'property' | 'general_liability'
export type PolicyStatus = 'active' | 'cancelled'

// What the screens show for each value. Record<...> makes TypeScript insist on every value.
export const LINE_OF_BUSINESS_LABELS: Record<LineOfBusiness, string> = {
  auto: 'Auto',
  property: 'Property',
  general_liability: 'General liability',
}
export const POLICY_STATUS_LABELS: Record<PolicyStatus, string> = {
  active: 'Active',
  cancelled: 'Cancelled',
}

export interface PolicyInfo {
  id: number
  organization_id: number
  policy_number: string
  insured_name: string
  line_of_business: LineOfBusiness
  effective_date: string // "YYYY-MM-DD": JSON has no date type
  expiration_date: string
  status: PolicyStatus
}

export interface CreatePolicyRequest {
  policy_number: string
  insured_name: string
  line_of_business: LineOfBusiness
  effective_date: string
  expiration_date: string
}

// A full replacement of the editable fields; cancelling is status "cancelled".
export interface UpdatePolicyRequest extends CreatePolicyRequest {
  status: PolicyStatus
}

export interface PolicyListParams {
  page_number: number
  page_size: number
  search?: string
  status?: PolicyStatus
  line_of_business?: LineOfBusiness
}

export async function listPolicies(params: PolicyListParams): Promise<Page<PolicyInfo>> {
  // axios leaves out params that are undefined, so an unused filter isn't sent at all.
  const response = await apiClient.get<Page<PolicyInfo>>('/policies', { params })
  return response.data
}

export async function getPolicy(policyId: number): Promise<PolicyInfo> {
  const response = await apiClient.get<PolicyInfo>(`/policies/${policyId}`)
  return response.data
}

export async function createPolicy(request: CreatePolicyRequest): Promise<PolicyInfo> {
  const response = await apiClient.post<PolicyInfo>('/policies', request)
  return response.data
}

export async function updatePolicy(
  policyId: number,
  request: UpdatePolicyRequest,
): Promise<PolicyInfo> {
  const response = await apiClient.put<PolicyInfo>(`/policies/${policyId}`, request)
  return response.data
}
