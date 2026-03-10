import axios, { AxiosError } from 'axios';
import { useAuthStore } from '../stores/auth';
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
export const apiClient = axios.create({ baseURL: API_BASE_URL, headers: { 'Content-Type': 'application/json' } });
apiClient.interceptors.request.use((config) => { const token = useAuthStore.getState().token; if (token) config.headers.Authorization = `Bearer ${token}`; return config; });
apiClient.interceptors.response.use((r) => r, async (error: AxiosError) => { if (error.response?.status === 401) { useAuthStore.getState().clearAuth(); window.location.href = '/auth/login'; } return Promise.reject(error); });
export const api = { get: <T>(url: string, params?: object) => apiClient.get<T>(url, { params }).then((r) => r.data), post: <T>(url: string, data?: object) => apiClient.post<T>(url, data).then((r) => r.data), patch: <T>(url: string, data?: object) => apiClient.patch<T>(url, data).then((r) => r.data), delete: <T>(url: string) => apiClient.delete<T>(url).then((r) => r.data) };
