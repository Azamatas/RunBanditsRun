import { test, expect } from "@playwright/test";
import { loginFreshUser, createActivityForUser, registerFresh } from "../helpers/auth";

test.describe("Feed", () => {
  test("greeting includes the current username", async ({ page, request }) => {
    const user = await loginFreshUser(page, request, "feed_greeting");
    await page.goto("/feed");
    await expect(page.locator(".feed-greeting")).toContainText(user.username);
  });

  test("renders activity cards after creating an activity", async ({ page, request }) => {
    const user = await loginFreshUser(page, request, "feed_activities");
    await createActivityForUser(request, user.access_token);
    await page.goto("/feed");
    await expect(page.locator(".activity-card").first()).toBeVisible();
  });

  test("clicking Kudos increments count and toggles back when clicked again", async ({ page, request }) => {
    const user1 = await registerFresh(request, "feed_kudos_1");
    const user2 = await registerFresh(request, "feed_kudos_2");
    await createActivityForUser(request, user2.access_token);
    await loginFreshUser(page, request, "feed_kudos_1");
    await page.goto("/feed");

    await expect(page.locator(".activity-card").first()).toBeVisible({ timeout: 10000 });

    const card = page.locator(".activity-card").filter({ has: page.getByRole("button", { name: /kudos/i }) }).first();
    await expect(card).toBeVisible();

    const kudosBtn = card.getByRole("button", { name: /kudos/i });
    const initialText = await kudosBtn.textContent();
    const initial = parseInt((initialText ?? "").match(/(\d+)/)?.[1] ?? "0", 10);

    await kudosBtn.click();
    await expect(kudosBtn).toContainText(`${initial + 1}`);
    await expect(kudosBtn).toHaveClass(/active/);

    await kudosBtn.click();
    await expect(kudosBtn).toContainText(`${initial}`);
    await expect(kudosBtn).not.toHaveClass(/active/);
  });

  test("clicking an activity title navigates to its detail page", async ({ page, request }) => {
    const user = await loginFreshUser(page, request, "feed_nav");
    const activity = await createActivityForUser(request, user.access_token);
    await page.goto("/feed");

    await expect(page.locator(".activity-card").first()).toBeVisible({ timeout: 10000 });
    const titleLink = page.locator(".activity-card-title").first();
    const expectedTitle = await titleLink.textContent();
    await titleLink.click();
    await expect(page).toHaveURL(/\/activities\/\d+$/);
    await expect(page.getByRole("heading", { name: expectedTitle?.trim() ?? "" })).toBeVisible();
  });

  test("Load More appends a second page without dropping the first", async ({ page, request }) => {
    const user = await loginFreshUser(page, request, "feed_paginate");
    // Create 15+ activities via API
    for (let i = 0; i < 15; i++) {
      await createActivityForUser(request, user.access_token, { title: `Paginate_${i}` });
    }
    await page.goto("/feed");

    await expect(page.locator(".activity-card").first()).toBeVisible({ timeout: 10000 });
    const before = await page.locator(".activity-card").count();

    const loadMore = page.getByRole("button", { name: /load more/i });
    await expect(loadMore).toBeVisible();
    await loadMore.click();
    await expect.poll(async () => page.locator(".activity-card").count()).toBeGreaterThan(before);
  });
});
