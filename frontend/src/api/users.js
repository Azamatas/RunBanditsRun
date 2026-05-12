import client from "./client";

export const getMe = () => client.get("/users/me").then((r) => r.data);
export const getUser = (id) => client.get(`/users/${id}`).then((r) => r.data);
export const updateMe = (data) => client.patch("/users/me", data).then((r) => r.data);
export const followUser = (id) => client.post(`/users/${id}/follow`).then((r) => r.data);
export const acceptFollow = (id) => client.post(`/users/${id}/accept`).then((r) => r.data);
export const getStats = () => client.get("/stats/me").then((r) => r.data);
export const searchUsers = (q) => client.get("/users/search", { params: { q } }).then((r) => r.data);
export const getFollowing = () => client.get("/users/me/following").then((r) => r.data);
export const getPendingRequests = () => client.get("/users/me/requests").then((r) => r.data);
