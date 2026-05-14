import { expect } from "@playwright/test";

export const SEEDED = {
  testUser: { email: "test@test.com", password: "Test1234", username: "test_user" },
  marc:     { email: "marc@example.com", password: "Password1", username: "marc_runner" },
  lisa:     { email: "lisa@example.com", password: "Password1", username: "lisa_pace" },
  tom:      { email: "tom@example.com",  password: "Password1", username: "tom_trails" },
  nina:     { email: "nina@example.com", password: "Password1", username: "nina_fast" },
  alex:     { email: "alex@example.com", password: "Password1", username: "alex_grind" },
};

/**
 * Log in by hitting the API and injecting the token into localStorage
 * BEFORE the SPA boots, so AuthContext picks it up on mount.
 */
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

/**
 * Register a brand-new user via the API. Returns credentials + tokens.
 * Auto-generates a unique email/username so re-runs don't collide.
 */
export async function registerFresh(request, prefix = "pw") {
  const stamp = Date.now() + Math.floor(Math.random() * 1000);
  const creds = {
    username: `${prefix}_${stamp}`,
    email: `${prefix}_${stamp}@test.com`,
    password: "Playwright1",
  };
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
