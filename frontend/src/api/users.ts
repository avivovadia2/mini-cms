import { apiClient } from './client'

// Mirror the backend schemas: UserInfo and AddUserRequest (app/modules/users/schemas) and
// Page (app/schemas.py).

export interface UserInfo {
  id: number
  organization_id: number
  email: string
  full_name: string
  is_active: boolean
}

export interface Page<T> {
  results: T[]
  total_count: number
}

export interface AddUserRequest {
  email: string
  full_name: string
  password: string
}

export async function listUsers(pageNumber: number, pageSize: number): Promise<Page<UserInfo>> {
  const response = await apiClient.get<Page<UserInfo>>('/users', {
    params: { page_number: pageNumber, page_size: pageSize },
  })
  return response.data
}

export async function addUser(request: AddUserRequest): Promise<UserInfo> {
  const response = await apiClient.post<UserInfo>('/users', request)
  return response.data
}
