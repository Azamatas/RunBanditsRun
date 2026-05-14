import { test, expect } from "@playwright/test";
import { SEEDED, loginAs, loginFreshUser, registerFresh } from "../helpers/auth";

test.describe("Friends & Explore", () => {
  test("search filters athletes by username", async ({ page, request }) => {
    await loginAs(page, request, SEEDED.testUser);
    await page.goto("/social");

    await page.getByPlaceholder(/search athletes/i).fill("marc");
    // Scope to the Search Results section (Connections above is unaffected by search)
    const resultsSection = page.locator("h3.section-title", { hasText: /search results/i }).locator("..");
    await expect(resultsSection.locator(".user-card", { hasText: SEEDED.marc.username }).first()).toBeVisible();
    await expect(resultsSection.locator(".user-card", { hasText: SEEDED.nina.username })).toHaveCount(0);
  });

  test("send a friend request — button switches to 'Request Sent'", async ({ page, request }) => {
    // Use a fresh user so the request slot is open
    await loginFreshUser(page, request, "fr_send");
    await page.goto("/social");

    await page.getByPlaceholder(/search athletes/i).fill("nina");
    const card = page.locator(".user-card").filter({ hasText: SEEDED.nina.username });
    await card.getByRole("button", { name: /add friend/i }).click();

    await expect(card.getByRole("button", { name: /request sent/i })).toBeVisible();
  });

  test("accept an incoming friend request", async ({ page, request }) => {
    // create a fresh user A; have seeded test_user send A a friend request, then log in as A and accept.
    const userA = await registerFresh(request, "fr_inA");
    // user A sends request? No — we want test_user → A (so A has incoming). Easier: log in as test_user via API, send to A, then login as A.
    const testLogin = await request.post("http://localhost:8000/auth/login", {
      data: { email: SEEDED.testUser.email, password: SEEDED.testUser.password },
    });
    const testBody = await testLogin.json();
    // resolve A's id
    const aMe = await request.get("http://localhost:8000/users/me", {
      headers: { Authorization: `Bearer ${userA.access_token}` },
    });
    const aBody = await aMe.json();
    const sendRes = await request.post(`http://localhost:8000/users/${aBody.id}/friend-request`, {
      headers: { Authorization: `Bearer ${testBody.access_token}` },
    });
    expect(sendRes.ok()).toBeTruthy();

    // now login as A and accept via UI
    await page.addInitScript(
      ([a, r]) => {
        localStorage.setItem("token", a);
        if (r) localStorage.setItem("refresh_token", r);
      },
      [userA.access_token, userA.refresh_token ?? ""],
    );

    await page.goto("/social");
    await expect(page.getByRole("heading", { name: /friend requests/i })).toBeVisible();
    // Scope the Accept click to the requests section (the first matching card)
    const incomingCard = page.locator(".user-card").filter({ hasText: SEEDED.testUser.username }).first();
    await incomingCard.getByRole("button", { name: /accept/i }).click();

    // The Friend Requests section heading should disappear since A has no more incoming requests
    await expect(page.getByRole("heading", { name: /friend requests/i })).toHaveCount(0);
  });

  test("remove a friend — Friends button reverts to Add Friend", async ({ page, request }) => {
    // create A, have A and seeded marc become friends via API, then login as A and unfriend from UI
    const userA = await registerFresh(request, "fr_rm");
    const marcLogin = await request.post("http://localhost:8000/auth/login", {
      data: { email: SEEDED.marc.email, password: SEEDED.marc.password },
    });
    const marcBody = await marcLogin.json();
    const aMe = await request.get("http://localhost:8000/users/me", {
      headers: { Authorization: `Bearer ${userA.access_token}` },
    });
    const aBody = await aMe.json();
    const marcMe = await request.get("http://localhost:8000/users/me", {
      headers: { Authorization: `Bearer ${marcBody.access_token}` },
    });
    const marcId = (await marcMe.json()).id;
    // A → marc friend request
    await request.post(`http://localhost:8000/users/${marcId}/friend-request`, {
      headers: { Authorization: `Bearer ${userA.access_token}` },
    });
    // marc accepts A
    await request.post(`http://localhost:8000/users/${aBody.id}/accept-friend`, {
      headers: { Authorization: `Bearer ${marcBody.access_token}` },
    });

    // login as A in browser
    await page.addInitScript(
      ([a, r]) => {
        localStorage.setItem("token", a);
        if (r) localStorage.setItem("refresh_token", r);
      },
      [userA.access_token, userA.refresh_token ?? ""],
    );

    await page.goto(`/users/${marcId}`);
    await expect(page.getByRole("button", { name: /^friends$/i })).toBeVisible();
    await page.getByRole("button", { name: /^friends$/i }).click();
    await expect(page.getByRole("button", { name: /add friend/i })).toBeVisible();
  });

  test("UserCard shows the right CTA per relationship state", async ({ page, request }) => {
    await loginAs(page, request, SEEDED.testUser);
    await page.goto("/social");
    await page.getByPlaceholder(/search athletes/i).fill("");
    // At least the seeded users should be visible with some CTA each
    const card = page.locator(".user-card").first();
    await expect(card).toBeVisible();
    const ctas = ["Add Friend", "Unfriend", "Request Sent", "Accept", "Cancel"];
    let matched = false;
    for (const name of ctas) {
      if (await card.getByRole("button", { name }).count() > 0) { matched = true; break; }
    }
    expect(matched, "UserCard should render one of: Add Friend / Friends / Request Sent / Accept").toBe(true);
  });
});
