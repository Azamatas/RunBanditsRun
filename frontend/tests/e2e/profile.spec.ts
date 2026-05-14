import { test, expect } from "@playwright/test";
import { loginFreshUser, createActivityForUser, registerFresh } from "../helpers/auth";
import { unique } from "../helpers/data";

test.describe("Profile", () => {
  test("own profile renders avatar, username and joined date", async ({ page, request }) => {
    const user = await loginFreshUser(page, request, "prof_basic");
    await page.goto("/profile");

    await expect(page.getByRole("heading", { name: user.username })).toBeVisible();
    await expect(page.getByText(/joined/i)).toBeVisible();
  });

  test("training totals show for a user with activities", async ({ page, request }) => {
    const user = await loginFreshUser(page, request, "prof_totals");
    await createActivityForUser(request, user.access_token);
    await page.goto("/profile");
    await expect(page.getByText(/training totals/i)).toBeVisible({ timeout: 10000 });
  });

  test("edit profile modal updates bio and location", async ({ page, request }) => {
    await loginFreshUser(page, request, "prof_edit");
    await page.goto("/profile");

    const newBio = unique("bio");
    const newLoc = unique("loc");

    await page.getByRole("button", { name: /^edit$/i }).click();
    await expect(page.getByRole("heading", { name: /edit profile/i })).toBeVisible();
    await page.getByPlaceholder("Portland, OR").fill(newLoc);
    await page.getByPlaceholder("Tell us about yourself...").fill(newBio);
    await page.getByRole("button", { name: /save changes/i }).click();

    await expect(page.getByRole("heading", { name: /edit profile/i })).toHaveCount(0);
    await expect(page.getByText(newBio)).toBeVisible();
    await expect(page.getByText(newLoc)).toBeVisible();
  });

  test("sport filter pills narrow the activity list", async ({ page, request }) => {
    const user = await loginFreshUser(page, request, "prof_filter");
    await createActivityForUser(request, user.access_token, { sport_type: "run" });
    await createActivityForUser(request, user.access_token, { sport_type: "ride" });
    await page.goto("/profile");

    await expect(page.getByRole("heading", { name: user.username })).toBeVisible();
    const cards = page.locator(".activity-card");
    await expect(cards.first()).toBeVisible({ timeout: 15000 });

    await page.locator(".filter-pill", { hasText: /^Run$/ }).click();
    const sportBadges = page.locator(".activity-card .badge-on-image");
    const count = await sportBadges.count();
    expect(count).toBeGreaterThan(0);
    for (let i = 0; i < count; i++) {
      await expect(sportBadges.nth(i)).toContainText(/run/i);
    }
  });

  test("logged-in user navigated to /users/<own-id> is redirected to /profile", async ({ page, request }) => {
    const user = await loginFreshUser(page, request, "prof_redir");
    const meRes = await request.get("http://localhost:8000/users/me", {
      headers: { Authorization: `Bearer ${user.access_token}` },
    });
    const meBody = await meRes.json();
    await page.goto(`/users/${meBody.id}`);
    await expect(page).toHaveURL(/\/profile$/);
  });
});
