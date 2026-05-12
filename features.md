# RunBanditsRun Features

## 1. Authentication & Account Setup
- Register (`POST /auth/register`)
- Log in (`POST /auth/login`)
- Refresh token (`POST /auth/refresh`)

## 2. Profile Management
- View own profile (`GET /users/me`)
- Edit profile: username, bio, location (`PATCH /users/me`)
- View another user's public profile (`GET /users/{id}`)

## 3. Social Graph
- Search users by username (`GET /users/search?q=`)
- Send follow request (`POST /users/{id}/follow`)
- Accept follow request (`POST /users/{id}/accept`)
- View pending requests received (`GET /users/me/requests`)
- View pending requests sent (`GET /users/me/sent-requests`)
- View followers (`GET /users/me/followers`)
- View following (`GET /users/me/following`)
- Unfollow (`DELETE /users/{id}/unfollow`)

## 4. Activity CRUD
- Create activity: title, sport type, distance, duration, elevation, polyline, visibility, tagged athletes (`POST /activities/`)
- View activity (`GET /activities/{id}`)
- Edit activity (`PATCH /activities/{id}`)
- Delete activity (`DELETE /activities/{id}`)
- Browse activities list with filters (`GET /activities/`)
- View another user's visible activities (`GET /users/{id}/activities`)

## 5. Activity Feed
- Personalized feed of friends' + public activities (`GET /feed/`)

## 6. Kudos
- Give kudos (`POST /activities/{id}/kudos`)
- Remove kudos (`DELETE /activities/{id}/kudos`)

## 7. Segments & Leaderboards
- Browse segments (`GET /segments/`)
- View segment detail (`GET /segments/{id}`)
- Create segment (`POST /segments/`)
- View segment leaderboard (`GET /segments/{id}/leaderboard`)
- View own efforts on a segment (`GET /segments/{id}/efforts`)

## 8. Personal Statistics
- Aggregated stats per sport: count, distance, elevation, duration (`GET /stats/me`)
- Personal records on segments (`GET /stats/me`, `personal_records`)

## 9. Map Visualization
- Activity route rendering via polyline data

## Visibility Rules
- **Public**: visible to everyone
- **Friends**: visible to owner + accepted friends
- **Private**: owner only