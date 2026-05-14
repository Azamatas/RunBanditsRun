import { test, expect } from "@playwright/test";
import { SEEDED, loginAs } from "../helpers/auth";

test.describe("Feed", () => {
  test.beforeEach(async ({ page, request }) => {
    await loginAs(page, request, SEEDED.testUser);
  });

  test("renders activity cards from the seeded feed", async ({ page }) => {
    await page.goto("/feed");
    await expect(page.locator(".activity-card").first()).toBeVisible();
    expect(await page.locator(".activity-card").count()).toBeGreaterThan(0);
  });

  test("greeting includes the current username", async ({ page }) => {
    await page.goto("/feed");
    await expect(page.locator(".feed-greeting")).toContainText(SEEDED.testUser.username);
  });

  test("clicking Kudos increments count and toggles back when clicked again", async ({ page }) => {
    await page.goto("/feed");
    // pick a card that has a Kudos button (i.e. not owned by current user)
    const card = page.locator(".activity-card").filter({ has: page.getByRole("button", { name: /kudos/i }) }).first();
    await expect(card).toBeVisible();

    const kudosBtn = card.getByRole("button", { name: /kudos/i });
    const initialText = await kudosBtn.textContent();
    const initial = parseInt((initialText ?? "").match(/\((\d+)\)/)?.[1] ?? "0", 10);

    await kudosBtn.click();
    await expect(kudosBtn).toContainText(`(${initial + 1})`);
    await expect(kudosBtn).toHaveClass(/active/);

    await kudosBtn.click();
    await expect(kudosBtn).toContainText(`(${initial})`);
    await expect(kudosBtn).not.toHaveClass(/active/);
  });

  test("clicking an activity title navigates to its detail page", async ({ page }) => {
    await page.goto("/feed");
    const titleLink = page.locator(".activity-card-title").first();
    await expect(titleLink).toBeVisible();
    const expectedTitle = await titleLink.textContent();
    await titleLink.click();
    await expect(page).toHaveURL(/\/activities\/\d+$/);
    await expect(page.getByRole("heading", { name: expectedTitle?.trim() ?? "" })).toBeVisible();
  });

  test("Load More appends a second page without dropping the first", async ({ page }) => {
    await page.goto("/feed");
    const loadMore = page.getByRole("button", { name: /load more/i });
    if (!(await loadMore.isVisible().catch(() => false))) {
      test.skip(true, "Not enough activities to paginate");
    }
    const before = await page.locator(".activity-card").count();
    await loadMore.click();
    await expect.poll(async () => page.locator(".activity-card").count()).toBeGreaterThan(before);
  });
});
