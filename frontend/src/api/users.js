import client from "./client";

export const getMe = () => client.get("/users/me").then((r) => r.data);
export const getUser = (id) => client.get(`/users/${id}`).then((r) => r.data);
export const getUserActivities = (id, params = {}) => client.get(`/users/${id}/activities`, { params }).then((r) => r.data);
export const updateMe = (data) => client.patch("/users/me", data).then((r) => r.data);
export const sendFriendRequest = (id) => client.post(`/users/${id}/friend-request`).then((r) => r.data);
export const acceptFriendRequest = (id) => client.post(`/users/${id}/accept-friend`).then((r) => r.data);
export const removeFriend = (id) => client.delete(`/users/${id}/friend`).then((r) => r.data);
export const getStats = () => client.get("/stats/me").then((r) => r.data);
export const searchUsers = (q) => client.get("/users/search", { params: { q } }).then((r) => r.data);
export const getFriends = () => client.get("/users/me/friends").then((r) => r.data);
export const getIncomingFriendRequests = () => client.get("/users/me/friend-requests/incoming").then((r) => r.data);
export const getSentFriendRequests = () => client.get("/users/me/friend-requests/sent").then((r) => r.data);
