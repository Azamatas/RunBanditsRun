import { test, expect } from "@playwright/test";
import { SEEDED, loginAs, registerFresh, clearAuth } from "../helpers/auth.js";
import { unique } from "../helpers/data.js";

test.describe("Authentication", () => {
  test.beforeEach(async ({ page }) => {
    await clearAuth(page);
  });

  test("registers a new user and lands on /feed", async ({ page }) => {
    const username = unique("user");
    const email = `${username}@test.com`;

    await page.goto("/register");
    await page.getByPlaceholder("alex_runner").fill(username);
    await page.getByPlaceholder("you@example.com").fill(email);
    await page.getByPlaceholder("Choose a strong password").fill("Playwright1");
    await page.getByRole("button", { name: /create account/i }).click();

    await expect(page).toHaveURL(/\/feed$/);
  });

  test("rejects weak passwords on the register form", async ({ page }) => {
    await page.goto("/register");
    await page.getByPlaceholder("alex_runner").fill(unique("user"));
    await page.getByPlaceholder("you@example.com").fill("weakpw@test.com");
    await page.getByPlaceholder("Choose a strong password").fill("short");
    await expect(page.getByText(/at least 8 characters/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /create account/i })).toBeDisabled();
  });

  test("shows server error when registering a duplicate email", async ({ page, request }) => {
    const fresh = await registerFresh(request, "dup");

    await page.goto("/register");
    await page.getByPlaceholder("alex_runner").fill(unique("user"));
    await page.getByPlaceholder("you@example.com").fill(fresh.email);
    await page.getByPlaceholder("Choose a strong password").fill("Playwright1");
    await page.getByRole("button", { name: /create account/i }).click();

    await expect(page.locator(".error")).toBeVisible();
  });

  test("logs in seeded test_user successfully", async ({ page }) => {
    await page.goto("/login");
    await page.getByPlaceholder("you@example.com").fill(SEEDED.testUser.email);
    await page.getByPlaceholder("Your password").fill(SEEDED.testUser.password);
    await page.getByRole("button", { name: /^log in$/i }).click();

    await expect(page).toHaveURL(/\/feed$/);
  });

  test("shows error on wrong credentials", async ({ page }) => {
    await page.goto("/login");
    await page.getByPlaceholder("you@example.com").fill(SEEDED.testUser.email);
    await page.getByPlaceholder("Your password").fill("WrongPassword99");
    await page.getByRole("button", { name: /^log in$/i }).click();

    await expect(page.locator(".error")).toBeVisible();
    await expect(page).toHaveURL(/\/login$/);
  });

  test("login form has required attributes", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByPlaceholder("you@example.com")).toHaveAttribute("required", "");
    await expect(page.getByPlaceholder("Your password")).toHaveAttribute("required", "");
  });

  test("logging out returns user to /login and hides nav links", async ({ page, request }) => {
    await loginAs(page, request, SEEDED.testUser);
    await page.goto("/feed");
    await expect(page.getByRole("link", { name: /^feed$/i })).toBeVisible();

    await page.getByRole("button", { name: /log out/i }).click();
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole("link", { name: /^feed$/i })).toHaveCount(0);
  });

  test("logged-in user visiting /login is redirected to /feed", async ({ page, request }) => {
    await loginAs(page, request, SEEDED.testUser);
    await page.goto("/login");
    await expect(page).toHaveURL(/\/feed$/);
  });

  test("logged-in user visiting /register is redirected to /feed", async ({ page, request }) => {
    await loginAs(page, request, SEEDED.testUser);
    await page.goto("/register");
    await expect(page).toHaveURL(/\/feed$/);
  });

  test("anonymous user visiting /feed is redirected to /login", async ({ page }) => {
    await page.goto("/feed");
    await expect(page).toHaveURL(/\/login$/);
  });

  test("anonymous user visiting /profile is redirected to /login", async ({ page }) => {
    await page.goto("/profile");
    await expect(page).toHaveURL(/\/login$/);
  });
});
