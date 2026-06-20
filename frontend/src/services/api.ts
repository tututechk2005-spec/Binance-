import axios, { AxiosError, AxiosInstance } from "axios";
import { useAuthStore } from "@/store/authStore";

const BASE_URL = import.meta.env.VITE_API_URL || "/api";

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as typeof error.config & { _retry?: boolean };
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refreshToken = useAuthStore.getState().refreshToken;
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refreshToken });
          useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
          original.headers!.Authorization = `Bearer ${data.access_token}`;
          return api(original);
        } catch {
          useAuthStore.getState().logout();
        }
      } else {
        useAuthStore.getState().logout();
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  register: (data: { username: string; email: string; password: string; full_name?: string }) =>
    api.post("/auth/register", data),
  logout: () => api.post("/auth/logout"),
  getMe: () => api.get("/auth/me"),
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post("/auth/change-password", data),
};

export const usersApi = {
  getProfile: () => api.get("/users/profile"),
  updateProfile: (data: Record<string, unknown>) => api.put("/users/profile", data),
  updateTradingSettings: (data: Record<string, unknown>) => api.put("/users/trading-settings", data),
  getApiKeys: () => api.get("/users/api-keys"),
  createApiKey: (data: Record<string, string>) => api.post("/users/api-keys", data),
  deleteApiKey: (id: string) => api.delete(`/users/api-keys/${id}`),
  verifyApiKey: (id: string) => api.post(`/users/api-keys/${id}/verify`),
};

export const signalsApi = {
  getSignals: (params?: Record<string, unknown>) => api.get("/signals", { params }),
  getSignal: (id: string) => api.get(`/signals/${id}`),
  getLatestActive: (limit?: number) => api.get("/signals/latest/active", { params: { limit } }),
  getStats: () => api.get("/signals/stats/summary"),
};

export const tradesApi = {
  getTrades: (params?: Record<string, unknown>) => api.get("/trades", { params }),
  getTrade: (id: string) => api.get(`/trades/${id}`),
  getPositions: () => api.get("/trades/positions"),
  getStats: () => api.get("/trades/stats"),
  closeTrade: (id: string) => api.post(`/trades/close/${id}`),
};

export const portfolioApi = {
  getOverview: () => api.get("/portfolio/overview"),
  getBalances: (keyId?: string) => api.get("/portfolio/balances", { params: { key_id: keyId } }),
  getPnlHistory: (days?: number) => api.get("/portfolio/pnl-history", { params: { days } }),
  getPerformance: () => api.get("/portfolio/performance"),
};

export const paymentsApi = {
  getPlans: () => api.get("/payments/plans"),
  getHistory: () => api.get("/payments/history"),
  createStripeSession: (data: Record<string, unknown>) => api.post("/payments/stripe/create-session", data),
  initiateMtn: (data: Record<string, unknown>) => api.post("/payments/mtn/initiate", data),
  initiateAirtel: (data: Record<string, unknown>) => api.post("/payments/airtel/initiate", data),
  getMtnStatus: (ref: string) => api.get(`/payments/mtn/status/${ref}`),
};

export const notificationsApi = {
  getAll: (params?: Record<string, unknown>) => api.get("/notifications", { params }),
  markRead: (id: string) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.put("/notifications/read-all"),
  getUnreadCount: () => api.get("/notifications/unread-count"),
};

export const adminApi = {
  getDashboard: () => api.get("/admin/dashboard"),
  getUsers: (params?: Record<string, unknown>) => api.get("/admin/users", { params }),
  toggleUserStatus: (id: string) => api.put(`/admin/users/${id}/status`),
  changeUserRole: (id: string, role: string) => api.put(`/admin/users/${id}/role`, null, { params: { role } }),
  getTrades: (params?: Record<string, unknown>) => api.get("/admin/trades", { params }),
  getSignals: (params?: Record<string, unknown>) => api.get("/admin/signals", { params }),
  getPayments: (params?: Record<string, unknown>) => api.get("/admin/payments", { params }),
  getAuditLogs: (params?: Record<string, unknown>) => api.get("/admin/audit-logs", { params }),
  getSystemLogs: (params?: Record<string, unknown>) => api.get("/admin/system-logs", { params }),
  getRevenueAnalytics: () => api.get("/admin/revenue-analytics"),
};

export default api;
