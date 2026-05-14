import client from "./client";
import type { TokenResponse, RegisterRequest, LoginRequest } from "../types/api";

export const register = (data: RegisterRequest): Promise<TokenResponse> =>
  client.post("/auth/register", data).then((r) => r.data);
export const login = (data: LoginRequest): Promise<TokenResponse> =>
  client.post("/auth/login", data).then((r) => r.data);
export const refreshToken = (refresh_token: string): Promise<TokenResponse> =>
  client.post("/auth/refresh", { refresh_token }).then((r) => r.data);
