# Frontend

React SPA built with Vite.

## Architecture

```
frontend/src/
  main.jsx           ReactDOM entry point
  App.jsx            Routes + NavBar
  index.css          Global styles + CSS custom properties
  api/               Axios API layer
    client.js          Axios instance with /api proxy, 401 refresh interceptor
    auth.js            login, register, refreshToken
    activities.js      CRUD + kudos endpoints
    feed.js            GET /feed/
    users.js           user profiles, follow/unfollow, search
    segments.js        CRUD + efforts
  context/
    AuthContext.jsx     Auth state provider (user, tokens, login/logout)
  pages/             Route components
    Feed.jsx            Activity feed (home)
    Login.jsx           /login
    Register.jsx        /register
    LogActivity.jsx     /log (create activity)
    ActivityDetail.jsx  /activities/:id (with kudos toggle)
    EditActivity.jsx    /activities/:id/edit
    Profile.jsx         /profile (own profile + stats)
    UserProfile.jsx     /users/:id (other user profile)
    Explore.jsx         /explore (user search)
    Segments.jsx         /segments (list + leaderboard)
    SegmentDetail.jsx    /segments/:id
    CreateSegment.jsx    /segments/new
  components/        Shared UI components
    ActivityCard.jsx     Feed card with kudos toggle + optimistic update
    ActivityFilters.jsx  Sport-type filter pills
    NavBar.jsx           Top nav with "+" dropdown (Log Activity / New Segment)
    ProtectedRoute.jsx   Auth guard wrapper
    EditProfileModal.jsx  Edit bio/location modal
    MapView.jsx          Leaflet map for polylines
    SportIcon.jsx        SVG sport icons + KudosIcon
    UserCard.jsx         User card with follow/unfollow + profile link
    LeaderboardTable.jsx Segment leaderboard table
  constants/
    images.js           Static image URLs (thumbnails, hero, empty states)
```

## Key patterns

- **API proxy:** Vite dev server proxies `/api` to `http://localhost:8000`, stripping the `/api` prefix. All API calls use `/api/...` paths.
- **Auth:** `AuthContext` stores access + refresh tokens in localStorage. `client.js` Axios interceptor auto-refreshes on 401, queues concurrent requests, retries.
- **Data fetching:** `@tanstack/react-query` for all server state. Mutations use optimistic updates with cache rollback on error.
- **Routing:** `react-router-dom` v6 with nested `ProtectedRoute` guards.
- **Styling:** Plain CSS with custom properties (see `index.css`). No CSS framework.