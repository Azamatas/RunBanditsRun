import client from "./client";
import type { Activity, ActivityCreatePayload, ActivityUpdatePayload } from "../types/api";

export const createActivity = (data: ActivityCreatePayload): Promise<Activity> =>
  client.post("/activities/", data).then((r) => r.data);
export const getActivity = (id: number | string): Promise<Activity> =>
  client.get(`/activities/${id}`).then((r) => r.data);
export const updateActivity = (id: number | string, data: ActivityUpdatePayload): Promise<Activity> =>
  client.patch(`/activities/${id}`, data).then((r) => r.data);
export const deleteActivity = (id: number | string) => client.delete(`/activities/${id}`);
export const giveKudos = (id: number | string) => client.post(`/activities/${id}/kudos`).then((r) => r.data);
export const removeKudos = (id: number | string) => client.delete(`/activities/${id}/kudos`);
