import { test, expect } from "@playwright/test";
import { SEEDED, loginAs, loginFreshUser } from "../helpers/auth";
import { unique } from "../helpers/data";

test.describe("Activities — create / view / edit / delete", () => {
  test("logs an activity and lands on its detail page", async ({ page, request }) => {
    await loginFreshUser(page, request, "act_create");
    await page.goto("/log");

    const title = unique("Run");
    await page.getByPlaceholder("Morning Run").fill(title);
    await page.getByPlaceholder("5.0").fill("8");
    await page.getByPlaceholder("30").fill("45");
    await page.getByPlaceholder("120").fill("60");

    await page.getByRole("button", { name: /save activity/i }).click();

    await expect(page).toHaveURL(/\/activities\/\d+$/);
    await expect(page.getByRole("heading", { name: title })).toBeVisible();
    await expect(page.getByText(/Kilometers/i)).toBeVisible();
  });

  test("activity detail shows stats for an owned activity and edit/delete controls", async ({ page, request }) => {
    await loginFreshUser(page, request, "act_view");
    await page.goto("/log");

    const title = unique("Tempo");
    await page.getByPlaceholder("Morning Run").fill(title);
    await page.getByPlaceholder("5.0").fill("10");
    await page.getByPlaceholder("30").fill("50");
    await page.getByRole("button", { name: /save activity/i }).click();
    await expect(page).toHaveURL(/\/activities\/\d+$/);

    // Owner sees Edit + Delete, no Give Kudos
    await expect(page.getByRole("link", { name: /^edit$/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /^delete$/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /give kudos/i })).toHaveCount(0);
  });

  test("editing an activity updates title and visibility", async ({ page, request }) => {
    await loginFreshUser(page, request, "act_edit");
    await page.goto("/log");

    const originalTitle = unique("Edit");
    await page.getByPlaceholder("Morning Run").fill(originalTitle);
    await page.getByPlaceholder("5.0").fill("5");
    await page.getByPlaceholder("30").fill("25");
    await page.getByRole("button", { name: /save activity/i }).click();
    await expect(page).toHaveURL(/\/activities\/\d+$/);

    await page.getByRole("link", { name: /^edit$/i }).click();
    await expect(page).toHaveURL(/\/edit$/);

    const newTitle = `${originalTitle} — edited`;
    // EditActivity title input has no placeholder, so target by required attr
    await page.locator("form input[required]").first().fill(newTitle);
    await page.getByRole("button", { name: /friends/i }).first().click();
    await page.getByRole("button", { name: /save changes/i }).click();

    await expect(page).toHaveURL(/\/activities\/\d+$/);
    await expect(page.getByRole("heading", { name: newTitle })).toBeVisible();
    await expect(page.getByText(/friends/i).last()).toBeVisible();
  });

  test("deleting an activity navigates back to the feed", async ({ page, request }) => {
    await loginFreshUser(page, request, "act_del");
    await page.goto("/log");
    await page.getByPlaceholder("Morning Run").fill(unique("Doomed"));
    await page.getByPlaceholder("5.0").fill("3");
    await page.getByPlaceholder("30").fill("20");
    await page.getByRole("button", { name: /save activity/i }).click();
    await expect(page).toHaveURL(/\/activities\/\d+$/);

    page.once("dialog", (d) => d.accept());
    await page.getByRole("button", { name: /^delete$/i }).click();
    await expect(page).toHaveURL(/\/feed$/);
  });

  test("a non-owner sees the Give Kudos button on someone else's activity", async ({ page, request }) => {
    await loginAs(page, request, SEEDED.testUser);
    await page.goto("/feed");

    const card = page.locator(".activity-card").filter({ has: page.getByRole("button", { name: /kudos/i }) }).first();
    await card.locator(".activity-card-title").click();
    await expect(page).toHaveURL(/\/activities\/\d+$/);
    await expect(page.getByRole("button", { name: /give kudos|kudos given/i })).toBeVisible();
  });

  test("required title prevents form submission", async ({ page, request }) => {
    await loginFreshUser(page, request, "act_req");
    await page.goto("/log");
    await page.getByRole("button", { name: /save activity/i }).click();
    // Should remain on /log because the required Title input blocks submission
    await expect(page).toHaveURL(/\/log$/);
  });
});
