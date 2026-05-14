import client from "./client";

export const getCommonActivities = () => client.get("/common-activities/").then((r) => r.data);
export const getCommonActivity = (id) => client.get(`/common-activities/${id}`).then((r) => r.data);
export const getCommonActivityLeaderboard = (id) =>
  client.get(`/common-activities/${id}/leaderboard`).then((r) => r.data);
