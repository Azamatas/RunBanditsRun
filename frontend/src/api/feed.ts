import client from "./client";
import type { Activity } from "../types/api";

export const getFeed = (offset = 0): Promise<Activity[]> =>
  client.get("/feed/", { params: { limit: 20, offset } }).then((r) => r.data);
