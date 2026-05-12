import client from "./client";

export const getSegments = () => client.get("/segments/").then((r) => r.data);
export const getSegment = (id) => client.get(`/segments/${id}`).then((r) => r.data);
export const getSegmentLeaderboard = (id) => client.get(`/segments/${id}/leaderboard`).then((r) => r.data);
export const createSegment = (data) => client.post("/segments/", data).then((r) => r.data);
