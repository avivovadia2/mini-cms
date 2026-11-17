import axios from 'axios'

// Single axios instance for the app. The relative baseURL goes through the Vite dev proxy, so the
// browser sees one origin and sends the session cookie anyway; withCredentials makes that explicit
// and keeps working if the API is ever served from another origin.
export const apiClient = axios.create({ baseURL: '/api', withCredentials: true })
