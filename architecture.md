# RunBanditsRun — Strava Clone: User Paths & Architecture

## 3 Main User Paths

### 1. Log an Activity
User authenticates - fills in activity details (type, title, distance, duration, elevation) - sets visibility (public / friends-only / private) - activity is saved with the user as owner - appears in the feeds of friends who have permission to see it

### 2. Explore the Social Feed
User opens home feed - sees activities from friends filtered by visibility rules - gives kudos on an activity - optionally drills into a specific activity to view its map, splits, and stats

### 3. View Personal Progress
User opens their profile - views their full activity history filtered by sport type or date range - sees aggregate stats (total distance, total elevation, personal records per segment) - views a specific segment effort and compares it against their own past efforts on that segment

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        React SPA                        │
│                                                         │
│  Pages: Login | Feed | Log Activity | Profile | Segment │
│  State: React Query (server state) + Context (auth)     │
└─────────────────────┬───────────────────────────────────┘
                      │  HTTP/REST (JSON)
                      │  Authorization: Bearer <JWT>
┌─────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend                       │
│                                                         │
│  Routers:                                               │
│    /auth          - register, login, refresh token      │
│    /users         - profile CRUD, friend requests       │
│    /activities    - create, read, update, delete        │
│    /feed          - paginated friend/public feed        │
│    /segments      - segment list, leaderboard           │
│    /stats         - personal aggregates, PRs            │
│                                                         │
│  Services (business logic layer):                       │
│    AuthService    - JWT issue & verify                  │
│    FeedService    - visibility-aware feed query         │
│    ActivityService - ownership check, visibility filter  │
│    StatsService   - aggregate & PR computation          │
│                                                         │
│  Middleware: JWT auth guard, CORS                       │
└─────────────────────┬───────────────────────────────────┘
                      │  SQLAlchemy ORM (session per request)
┌─────────────────────▼───────────────────────────────────┐
│                   SQLAlchemy Models                     │
│                                                         │
│  User            – id, username, email, password_hash,  │
│                    bio, location, created_at            │
│                                                         │
│  Friendship      - requester_id - addressee_id,         │
│                    status (pending / accepted)          │
│                                                         │
│  Activity        - id, owner_id (FK->User),              │
│                    title, sport_type, distance,         │
│                    duration, elevation, polyline,       │
│                    visibility (public/friends/private), │
│                    started_at, created_at               │
│                                                         │
│  ActivityAthlete - activity_id, user_id  - "with whom" │
│                    (many-to-many: friends in activity)  │
│                                                         │
│  Segment         – id, name, polyline, distance         │
│                                                         │
│  SegmentEffort   – id, segment_id, activity_id,         │
│                    athlete_id, elapsed_time, started_at │
│                                                         │
│  Kudos           – id, activity_id, user_id, created_at │
└─────────────────────────────────────────────────────────┘
```

---

## Activity Ownership & Friend Visibility

An activity has a single **owner** (`owner_id`) — the user who created it.

Other athletes can be **tagged into** the activity via the `ActivityAthlete` join table. This represents "run with friends" — tagged athletes see the activity on their profile even if they didn't log it themselves.

Visibility rules enforced by `ActivityService` on every read:

| Visibility | Who can see |
|---|---|
| `public` | Everyone, including unauthenticated users |
| `friends` | Owner + accepted friends of the owner |
| `private` | Owner only |

The feed query (`FeedService`) joins `Activity` - `Friendship` and filters by the requesting user's friend list and the activity's `visibility` field before returning results.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + React Query |
| Backend | FastAPI (Python) |
| ORM | SQLAlchemy |
| Auth | JWT (python-jose) + bcrypt |
| Hosting (frontend) | Vercel / Netlify |
| Hosting (backend + db) | Render / PythonAnywhere |

---

## Key Design Decisions

- **Pull-based feed**: the feed is computed at query time by joining activities of friends — simple to implement, no fan-out writes needed at this scale.
- **Friendship is bidirectional with status**: using a `status` column (pending/accepted) on a single directed row avoids duplicate rows and makes friend requests natural.
- **Activity visibility at the service layer**: visibility is checked in Python before returning data, keeping the rule in one place rather than scattered across queries.
- **SegmentEffort as a derived entity**: segment efforts are created when an activity is saved (matched against known segments), decoupling activity logging from segment tracking.
