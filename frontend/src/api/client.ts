import axios, { AxiosError, type AxiosRequestConfig, type InternalAxiosRequestConfig } from "axios";

const client = axios.create({ baseURL: "/api" });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token && config.headers) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

interface QueuedRequest {
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}

let isRefreshing = false;
let failedQueue: QueuedRequest[] = [];

function processQueue(error: unknown, token: string | null = null): void {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else if (token) prom.resolve(token);
  });
  failedQueue = [];
}

interface RetryConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryConfig | undefined;
    if (!originalRequest) return Promise.reject(error);

    if (error.response?.status === 401 && /^\/auth\/(login|register|refresh)/.test(originalRequest.url ?? "")) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        localStorage.removeItem("token");
        window.location.href = "/login";
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          if (originalRequest.headers) originalRequest.headers.Authorization = `Bearer ${token}`;
          return client(originalRequest as AxiosRequestConfig);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const res = await axios.post("/api/auth/refresh", { refresh_token: refreshToken });
        const { access_token, refresh_token: newRefresh } = res.data;
        localStorage.setItem("token", access_token);
        if (newRefresh) localStorage.setItem("refresh_token", newRefresh);
        processQueue(null, access_token);
        if (originalRequest.headers) originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return client(originalRequest as AxiosRequestConfig);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem("token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  },
);

export default client;
