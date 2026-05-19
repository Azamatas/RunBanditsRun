import client from "./client";
import type { CommonActivity, CommonActivityCreatePayload, LeaderboardEntry } from "../types/api";

export const getCommonActivities = (): Promise<CommonActivity[]> =>
  client.get("/common-activities/").then((r) => r.data);

export const getCommonActivity = (id: number | string): Promise<CommonActivity> =>
  client.get(`/common-activities/${id}`).then((r) => r.data);

export const getCommonActivityLeaderboard = (id: number | string): Promise<LeaderboardEntry[]> =>
  client.get(`/common-activities/${id}/leaderboard`).then((r) => r.data);

export const createCommonActivity = (data: CommonActivityCreatePayload): Promise<CommonActivity> =>
  client.post("/common-activities/", data).then((r) => r.data);
