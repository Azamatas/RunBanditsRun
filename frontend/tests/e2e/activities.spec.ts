import { test, expect } from "@playwright/test";
import { loginFreshUser, registerFresh, createActivityForUser } from "../helpers/auth";
import { unique } from "../helpers/data";

test.describe("Activities — create / view / edit / delete", () => {
  test("adds an activity and lands on its detail page", async ({ page, request }) => {
    await loginFreshUser(page, request, "act_create");
    await page.goto("/add-activity");

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
    await page.goto("/add-activity");

    const title = unique("Tempo");
    await page.getByPlaceholder("Morning Run").fill(title);
    await page.getByPlaceholder("5.0").fill("10");
    await page.getByPlaceholder("30").fill("50");
    await page.getByRole("button", { name: /save activity/i }).click();
    await expect(page).toHaveURL(/\/activities\/\d+$/);

    await expect(page.getByRole("link", { name: /^edit$/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /^delete$/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /give kudos/i })).toHaveCount(0);
  });

  test("editing an activity updates title and visibility", async ({ page, request }) => {
    await loginFreshUser(page, request, "act_edit");
    await page.goto("/add-activity");

    const originalTitle = unique("Edit");
    await page.getByPlaceholder("Morning Run").fill(originalTitle);
    await page.getByPlaceholder("5.0").fill("5");
    await page.getByPlaceholder("30").fill("25");
    await page.getByRole("button", { name: /save activity/i }).click();
    await expect(page).toHaveURL(/\/activities\/\d+$/);

    await page.getByRole("link", { name: /^edit$/i }).click();
    await expect(page).toHaveURL(/\/edit$/);

    const newTitle = `${originalTitle} — edited`;
    await page.locator("form input[required]").first().fill(newTitle);
    await page.getByRole("button", { name: /friends/i }).first().click();
    await page.getByRole("button", { name: /save changes/i }).click();

    await expect(page).toHaveURL(/\/activities\/\d+$/);
    await expect(page.getByRole("heading", { name: newTitle })).toBeVisible();
    await expect(page.getByText(/friends/i).last()).toBeVisible();
  });

  test("deleting an activity navigates back to the feed", async ({ page, request }) => {
    await loginFreshUser(page, request, "act_del");
    await page.goto("/add-activity");
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
    const user1 = await registerFresh(request, "kudos_owner");
    const activity = await createActivityForUser(request, user1.access_token);
    await loginFreshUser(page, request, "kudos_visitor");
    await page.goto(`/activities/${activity.id}`);

    await expect(page.getByRole("button", { name: /give kudos|kudos given/i })).toBeVisible();
  });

  test("required title prevents form submission", async ({ page, request }) => {
    await loginFreshUser(page, request, "act_req");
    await page.goto("/add-activity");
    await page.getByRole("button", { name: /save activity/i }).click();
    await expect(page).toHaveURL(/\/add-activity$/);
  });
});
