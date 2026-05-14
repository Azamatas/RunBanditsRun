import { http, HttpResponse } from "msw";
import {
  currentUser, users, activities, stats, segments, segmentEfforts,
  friendships, createActivity, enrichActivity, getFriendsOf,
  getPendingRequestsFor, addFriendship, acceptFriendship,
} from "./data";

const MOCK_TOKEN = "mock-jwt-token";
const userMap = Object.fromEntries(users.map((u) => [u.id, u]));

export const handlers = [
  http.post("/api/auth/register", () =>
    HttpResponse.json({ access_token: MOCK_TOKEN, token_type: "bearer" }),
  ),
  http.post("/api/auth/login", () =>
    HttpResponse.json({ access_token: MOCK_TOKEN, token_type: "bearer" }),
  ),

http.get("/api/users/me", () => HttpResponse.json(currentUser)),

  http.patch("/api/users/me", async ({ request }) => {
    const body = await request.json();
    Object.assign(currentUser, body);
    return HttpResponse.json(currentUser);
  }),

  http.get("/api/users/search", ({ request }) => {
    const url = new URL(request.url);
    const q = (url.searchParams.get("q") ?? "").toLowerCase();
    const results = users.filter(
      (u) => u.id !== currentUser.id && u.username.toLowerCase().includes(q),
    );
    return HttpResponse.json(results);
  }),

  http.get("/api/users/me/friends", () => {
    const friendIds = getFriendsOf(currentUser.id);
    return HttpResponse.json(friendIds.map((id) => userMap[id]).filter(Boolean));
  }),

  http.get("/api/users/me/friend-requests/incoming", () => {
    const pending = getPendingRequestsFor(currentUser.id);
    return HttpResponse.json(
      pending.map((f) => ({ ...f, requester: userMap[f.requester_id] })),
    );
  }),

  http.get("/api/users/:userId", ({ params }) => {
    const u = userMap[Number(params.userId)];
    if (!u) return new HttpResponse(null, { status: 404 });
    return HttpResponse.json(u);
  }),

  http.post("/api/users/:userId/friend-request", ({ params }) => {
    const id = Number(params.userId);
    addFriendship(currentUser.id, id);
    return HttpResponse.json({ status: "pending" }, { status: 201 });
  }),

  http.post("/api/users/:userId/accept-friend", ({ params }) => {
    const id = Number(params.userId);
    acceptFriendship(id, currentUser.id);
    return HttpResponse.json({ status: "accepted" });
  }),

  http.delete("/api/users/:userId/friend", () => {
    return new HttpResponse(null, { status: 204 });
  }),

  http.get("/api/feed/", ({ request }) => {
    const url = new URL(request.url);
    const limit = Number(url.searchParams.get("limit")) || 20;
    const offset = Number(url.searchParams.get("offset")) || 0;
    return HttpResponse.json(activities.slice(offset, offset + limit).map(enrichActivity));
  }),

  http.post("/api/activities/", async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(createActivity(body));
  }),

  http.get("/api/activities/:id", ({ params }) => {
    const activity = activities.find((a) => a.id === Number(params.id));
    if (!activity) return new HttpResponse(null, { status: 404 });
    return HttpResponse.json(enrichActivity(activity));
  }),

  http.patch("/api/activities/:id", async ({ params, request }) => {
    const activity = activities.find((a) => a.id === Number(params.id));
    if (!activity) return new HttpResponse(null, { status: 404 });
    Object.assign(activity, await request.json());
    return HttpResponse.json(enrichActivity(activity));
  }),

  http.delete("/api/activities/:id", ({ params }) => {
    const idx = activities.findIndex((a) => a.id === Number(params.id));
    if (idx === -1) return new HttpResponse(null, { status: 404 });
    activities.splice(idx, 1);
    return new HttpResponse(null, { status: 204 });
  }),

  http.post("/api/activities/:id/kudos", ({ params }) => {
    const activity = activities.find((a) => a.id === Number(params.id));
    if (!activity) return new HttpResponse(null, { status: 404 });
    activity.kudos_count += 1;
    return HttpResponse.json({ kudos_count: activity.kudos_count }, { status: 201 });
  }),

  http.delete("/api/activities/:id/kudos", ({ params }) => {
    const activity = activities.find((a) => a.id === Number(params.id));
    if (!activity) return new HttpResponse(null, { status: 404 });
    activity.kudos_count = Math.max(0, activity.kudos_count - 1);
    return new HttpResponse(null, { status: 204 });
  }),

  http.get("/api/stats/me", () => HttpResponse.json(stats)),

  http.get("/api/segments/", () => {
    const enriched = segments.map((seg) => {
      const myBest = segmentEfforts
        .filter((e) => e.segment_id === seg.id && e.athlete_id === currentUser.id)
        .sort((a, b) => a.elapsed_time - b.elapsed_time)[0];
      return { ...seg, my_best_time: myBest?.elapsed_time ?? null };
    });
    return HttpResponse.json(enriched);
  }),

  http.get("/api/segments/:id", ({ params }) => {
    const seg = segments.find((s) => s.id === Number(params.id));
    if (!seg) return new HttpResponse(null, { status: 404 });
    return HttpResponse.json(seg);
  }),

  http.get("/api/segments/:id/leaderboard", ({ params }) => {
    const segId = Number(params.id);
    const efforts = segmentEfforts
      .filter((e) => e.segment_id === segId)
      .sort((a, b) => a.elapsed_time - b.elapsed_time)
      .map((e, i) => ({
        rank: i + 1,
        athlete_id: e.athlete_id,
        athlete_username: userMap[e.athlete_id]?.username ?? "unknown",
        elapsed_time: e.elapsed_time,
        started_at: e.started_at,
        activity_id: e.activity_id,
      }));
    return HttpResponse.json(efforts);
  }),
];
