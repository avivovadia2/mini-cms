import axios from 'axios'

// Single axios instance for the app; relative baseURL works with the Vite dev proxy.
export const apiClient = axios.create({ baseURL: '/api' })
