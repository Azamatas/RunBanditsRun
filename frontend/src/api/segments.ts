import client from "./client";
import type { Segment, SegmentCreatePayload, LeaderboardEntry } from "../types/api";

export const getSegments = (): Promise<Segment[]> => client.get("/segments/").then((r) => r.data);
export const getSegment = (id: number | string): Promise<Segment> =>
  client.get(`/segments/${id}`).then((r) => r.data);
export const getSegmentLeaderboard = (id: number | string): Promise<LeaderboardEntry[]> =>
  client.get(`/segments/${id}/leaderboard`).then((r) => r.data);
export const createSegment = (data: SegmentCreatePayload): Promise<Segment> =>
  client.post("/segments/", data).then((r) => r.data);
