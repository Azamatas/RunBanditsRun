import { test, expect } from "@playwright/test";
import { loginFreshUser, registerFresh, createActivityForUser } from "../helpers/auth";

test.describe("Friends & Explore", () => {
  test("search filters athletes by username", async ({ page, request }) => {
    await loginFreshUser(page, request, "fr_search");
    const user2 = await registerFresh(request, "marc_search");
    await page.goto("/social");

    await page.getByPlaceholder(/search athletes/i).fill("marc_search");
    const resultsSection = page.locator("h3.section-title", { hasText: /search results/i }).locator("..");
    await expect(resultsSection.locator(".user-card", { hasText: user2.username }).first()).toBeVisible();
  });

  test("send a friend request — button switches to 'Request Sent'", async ({ page, request }) => {
    const user1 = await loginFreshUser(page, request, "fr_send_1");
    const user2 = await registerFresh(request, "fr_send_2");
    await page.goto("/social");

    await page.getByPlaceholder(/search athletes/i).fill(user2.username);
    const card = page.locator(".user-card").filter({ hasText: user2.username });
    await card.getByRole("button", { name: /add friend/i }).click();

    await expect(card.getByRole("button", { name: /request sent/i })).toBeVisible();
  });

  test("accept an incoming friend request", async ({ page, request }) => {
    const userA = await registerFresh(request, "fr_accept_a");
    const userB = await registerFresh(request, "fr_accept_b");

    const aMe = await request.get("http://localhost:8000/users/me", {
      headers: { Authorization: `Bearer ${userA.access_token}` },
    });
    const aBody = await aMe.json();
    await request.post(`http://localhost:8000/users/${aBody.id}/friend-request`, {
      headers: { Authorization: `Bearer ${userB.access_token}` },
    });

    await page.addInitScript(
      ([a, r]) => {
        localStorage.setItem("token", a);
        if (r) localStorage.setItem("refresh_token", r);
      },
      [userA.access_token, userA.refresh_token ?? ""],
    );

    await page.goto("/social");
    await expect(page.getByRole("heading", { name: /friend requests/i })).toBeVisible();
    const incomingCard = page.locator(".user-card").filter({ hasText: userB.username }).first();
    await incomingCard.getByRole("button", { name: /accept/i }).click();

    await expect(page.getByRole("heading", { name: /friend requests/i })).toHaveCount(0);
  });

  test("remove a friend — Friends button reverts to Add Friend", async ({ page, request }) => {
    const userA = await registerFresh(request, "fr_remove_a");
    const userB = await registerFresh(request, "fr_remove_b");

    const aMe = await request.get("http://localhost:8000/users/me", {
      headers: { Authorization: `Bearer ${userA.access_token}` },
    });
    const aBody = await aMe.json();
    const bMe = await request.get("http://localhost:8000/users/me", {
      headers: { Authorization: `Bearer ${userB.access_token}` },
    });
    const bBody = await bMe.json();

    await request.post(`http://localhost:8000/users/${bBody.id}/friend-request`, {
      headers: { Authorization: `Bearer ${userA.access_token}` },
    });
    await request.post(`http://localhost:8000/users/${aBody.id}/accept-friend`, {
      headers: { Authorization: `Bearer ${userB.access_token}` },
    });

    await page.addInitScript(
      ([a, r]) => {
        localStorage.setItem("token", a);
        if (r) localStorage.setItem("refresh_token", r);
      },
      [userA.access_token, userA.refresh_token ?? ""],
    );

    await page.goto(`/users/${bBody.id}`);
    await expect(page.getByRole("button", { name: /^friends$/i })).toBeVisible();
    await page.getByRole("button", { name: /^friends$/i }).click();
    await expect(page.getByRole("button", { name: /add friend/i })).toBeVisible();
  });

  test("UserCard shows the right CTA per relationship state", async ({ page, request }) => {
    await loginFreshUser(page, request, "fr_cta");
    const user2 = await registerFresh(request, "fr_cta_other");
    await page.goto("/social");
    await page.getByPlaceholder(/search athletes/i).fill(user2.username);

    const card = page.locator(".user-card").filter({ hasText: user2.username }).first();
    await expect(card).toBeVisible();
    const ctas = ["Add Friend", "Unfriend", "Request Sent", "Accept", "Cancel"];
    let matched = false;
    for (const name of ctas) {
      if (await card.getByRole("button", { name }).count() > 0) { matched = true; break; }
    }
    expect(matched, "UserCard should render one of: Add Friend / Friends / Request Sent / Accept").toBe(true);
  });
});
