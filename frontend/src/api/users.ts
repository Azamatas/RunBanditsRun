import client from "./client";
import type { User, Activity, Stats, FriendRequest } from "../types/api";

export const getMe = (): Promise<User> => client.get("/users/me").then((r) => r.data);
export const getUser = (id: number | string): Promise<User> => client.get(`/users/${id}`).then((r) => r.data);
export const getUserActivities = (id: number | string, params: Record<string, unknown> = {}): Promise<Activity[]> =>
  client.get(`/users/${id}/activities`, { params }).then((r) => r.data);
export const updateMe = (data: Partial<User>): Promise<User> => client.patch("/users/me", data).then((r) => r.data);
export const sendFriendRequest = (id: number): Promise<{ status: string }> =>
  client.post(`/users/${id}/friend-request`).then((r) => r.data);
export const acceptFriendRequest = (id: number): Promise<{ status: string }> =>
  client.post(`/users/${id}/accept-friend`).then((r) => r.data);
export const removeFriend = (id: number): Promise<void> => client.delete(`/users/${id}/friend`).then((r) => r.data);
export const getStats = (): Promise<Stats> => client.get("/stats/me").then((r) => r.data);
export const searchUsers = (q: string): Promise<User[]> =>
  client.get("/users/search", { params: { q } }).then((r) => r.data);
export const getFriends = (): Promise<User[]> => client.get("/users/me/friends").then((r) => r.data);
export const getIncomingFriendRequests = (): Promise<FriendRequest[]> =>
  client.get("/users/me/friend-requests/incoming").then((r) => r.data);
export const getSentFriendRequests = (): Promise<FriendRequest[]> =>
  client.get("/users/me/friend-requests/sent").then((r) => r.data);
