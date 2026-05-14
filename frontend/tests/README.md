# Frontend E2E tests (Playwright)

End-to-end test suite covering every main user flow. Runs in a real Chromium
against the **actual** backend at `http://localhost:8000` and the dev frontend
at `http://localhost:5173`.

## Prerequisites

1. **Backend running**
   ```bash
   # from repo root
   source .venv/bin/activate
   python3 -m uvicorn backend.main:app --reload
   ```
   Postgres must be up too (the docker-compose db, or Homebrew postgres with
   the `runbandits` user/database).

2. **Frontend dev server running**
   ```bash
   cd frontend && npm run dev
   ```

3. **Database seeded** (only needed once, or to reset state):
   ```bash
   # from repo root
   .venv/bin/python3 seed.py
   .venv/bin/python3 /tmp/seed_extras.py   # extras script created during setup
   ```
   Seed creates: `test_user` (`test@test.com` / `Test1234`) plus 5 named
   athletes (`marc_runner`, `lisa_pace`, `tom_trails`, `nina_fast`, `alex_grind`,
   all with password `Password1`), ~48 activities, kudos, friendships, and 4
   segments with leaderboards.

4. **Chromium installed** (one-time):
   ```bash
   cd frontend && npx playwright install chromium
   ```

## Running

```bash
cd frontend

npm run test:e2e             # headless full suite
npm run test:e2e:headed      # with a visible browser
npm run test:e2e:ui          # interactive UI mode (best for debugging)
npm run test:e2e -- auth     # run only auth.spec.js
npm run test:e2e -- --grep "logs an activity"  # filter by test title

npm run test:e2e:report      # open last HTML report
```

After a failed run the HTML report lives at `frontend/playwright-report/` and
traces/screenshots are under `frontend/test-results/`.

## Layout

```
tests/
├── README.md
├── helpers/
│   ├── auth.js     # loginAs, registerFresh, loginFreshUser, clearAuth, SEEDED creds
│   └── data.js     # unique(), activityPayload(), segmentPayload()
└── e2e/
    ├── auth.spec.js          # register, login, logout, redirects
    ├── feed.spec.js          # feed render, kudos, pagination, navigation
    ├── activities.spec.js    # create / view / edit / delete / kudos visibility
    ├── profile.spec.js       # own profile, stats, edit modal, filters
    └── friends.spec.js       # search, request, accept, remove
```

## Conventions

- **Selectors**: prefer `getByRole` + accessible name; fall back to visible
  text. Avoid CSS selectors for things users see; use them only for
  structural assertions (`.activity-card`, `.error`).
- **State-changing tests** create a fresh user via `loginFreshUser()` so the
  seeded users stay clean.
- **Read-only tests** reuse seeded users via `loginAs(page, request, SEEDED.x)`.
- **`workers: 1`** is set in `playwright.config.js` to avoid race conditions
  on the shared database. Bump this up if you want to parallelize specific
  spec files later — annotate them with
  `test.describe.configure({ mode: "parallel" })`.
- **Login speed**: `loginAs` hits the API directly and injects the token via
  `addInitScript` — no UI form-filling round-trip. ~5× faster than form login.

## Sanity check before running

```bash
curl -fsS http://localhost:8000/ >/dev/null && echo "backend ok"
curl -fsS http://localhost:5173/ >/dev/null && echo "frontend ok"
```

## When something flakes

1. Open the report — `npm run test:e2e:report` — and inspect the trace.
2. If a selector matches multiple elements, narrow it with `.first()`,
   `.filter({ hasText: ... })`, or a parent locator.
3. If a test needs a stable identifier, add a `data-testid="..."` to the
   component and select with `page.getByTestId(...)`.
4. The DB accumulates test data over time. Re-seed when it gets noisy:
   ```bash
   .venv/bin/python3 seed.py && .venv/bin/python3 /tmp/seed_extras.py
   ```
bin/python3 /tmp/seed_extras.py
   ```
