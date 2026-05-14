import { test, expect } from "@playwright/test";
import { SEEDED, loginAs } from "../helpers/auth";
import { unique } from "../helpers/data";

test.describe("Segments", () => {
  test.beforeEach(async ({ page, request }) => {
    await loginAs(page, request, SEEDED.testUser);
  });

  test("segments page lists seeded segments", async ({ page }) => {
    await page.goto("/segments");
    await expect(page.getByRole("heading", { name: /popular segments/i })).toBeVisible();
    // Seed creates: Vondelpark Loop, Amstel Riverside Sprint, IJ Waterfront Run, Oosterpark Hill Climb
    await expect(page.getByRole("link", { name: /vondelpark loop/i })).toBeVisible();
  });

  test("clicking a segment navigates to its detail page with a leaderboard", async ({ page }) => {
    await page.goto("/segments");
    await page.getByRole("link", { name: /vondelpark loop/i }).click();
    await expect(page).toHaveURL(/\/segments\/\d+$/);
    await expect(page.getByRole("heading", { name: /vondelpark loop/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: /leaderboard/i })).toBeVisible();
    // Leaderboard table has athlete + time columns
    await expect(page.locator("table.leaderboard")).toBeVisible();
  });

  test("invalid segment id shows the error state", async ({ page }) => {
    await page.goto("/segments/999999");
    // React Query retries 3× with backoff before surfacing isError, so wait longer
    await expect(page.locator(".error")).toBeVisible({ timeout: 15000 });
  });

  test("create segment via the form succeeds", async ({ page }) => {
    await page.goto("/segments/new");
    const name = unique("Seg");
    await page.getByPlaceholder("Morning Hill Sprint").fill(name);
    await page.getByPlaceholder("5.0").fill("2.5");
    await page.getByRole("button", { name: /create segment/i }).click();
    await expect(page).toHaveURL(/\/segments\/\d+$/);
    await expect(page.getByRole("heading", { name })).toBeVisible();
  });
});
