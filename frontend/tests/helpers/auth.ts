import { expect } from "@playwright/test";
import { unique, activityPayload } from "./data";

export async function loginAs(page, request, { email, password }) {
  const res = await request.post("http://localhost:8000/auth/login", {
    data: { email, password },
  });
  expect(res.ok(), `login API failed for ${email}: ${res.status()}`).toBeTruthy();
  const body = await res.json();
  const access = body.access_token;
  const refresh = body.refresh_token ?? "";

  await page.addInitScript(
    ([a, r]) => {
      localStorage.setItem("token", a);
      if (r) localStorage.setItem("refresh_token", r);
    },
    [access, refresh],
  );
  return body;
}

export async function registerFresh(request, prefix = "pw") {
  const username = unique(prefix);
  const email = `${username}@test.com`;
  const creds = { username, email, password: "Playwright1" };
  const res = await request.post("http://localhost:8000/auth/register", { data: creds });
  expect(res.ok(), `register API failed: ${res.status()}`).toBeTruthy();
  const body = await res.json();
  return { ...creds, ...body };
}

export async function loginFreshUser(page, request, prefix = "pw") {
  const user = await registerFresh(request, prefix);
  await page.addInitScript(
    ([a, r]) => {
      localStorage.setItem("token", a);
      if (r) localStorage.setItem("refresh_token", r);
    },
    [user.access_token, user.refresh_token ?? ""],
  );
  return user;
}

export async function clearAuth(page) {
  await page.addInitScript(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
  });
}

export async function createActivityForUser(request, accessToken, overrides = {}) {
  const payload = {
    ...activityPayload(overrides),
    distance: 5000,
    duration: 1800,
    elevation: 100,
  };
  const res = await request.post("http://localhost:8000/activities", {
    headers: { Authorization: `Bearer ${accessToken}` },
    data: payload,
  });
  expect(res.ok(), `create activity failed: ${res.status()}`).toBeTruthy();
  const body = await res.json();
  return body;
}

export async function registerFreshUserWithActivity(request, prefix = "pw", activityOverrides = {}) {
  const user = await registerFresh(request, prefix);
  const activity = await createActivityForUser(request, user.access_token, activityOverrides);
  return { ...user, activityId: activity.id };
}

export async function getMe(request, accessToken) {
  const res = await request.get("http://localhost:8000/users/me", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  expect(res.ok(), `getMe API failed: ${res.status()}`).toBeTruthy();
  return await res.json();
}

export async function sendFriendRequest(request, accessToken, targetUserId) {
  const res = await request.post(`http://localhost:8000/users/${targetUserId}/friend-request`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  expect(res.ok(), `sendFriendRequest API failed: ${res.status()}`).toBeTruthy();
  return await res.json();
}

export async function acceptFriendRequest(request, accessToken, requesterUserId) {
  const res = await request.post(`http://localhost:8000/users/${requesterUserId}/accept-friend`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  expect(res.ok(), `acceptFriendRequest API failed: ${res.status()}`).toBeTruthy();
  return await res.json();
}

export async function establishFriendship(request, accessTokenA, accessTokenB) {
  const userA = await getMe(request, accessTokenA);
  const userB = await getMe(request, accessTokenB);
  await sendFriendRequest(request, accessTokenA, userB.id);
  await acceptFriendRequest(request, accessTokenB, userA.id);
  return { userA, userB };
}
