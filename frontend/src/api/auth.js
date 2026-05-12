import client from "./client";

export const register = (data) => client.post("/auth/register", data).then((r) => r.data);
export const login = (data) => client.post("/auth/login", data).then((r) => r.data);
export const refreshToken = (refresh_token) => client.post("/auth/refresh", { refresh_token }).then((r) => r.data);
