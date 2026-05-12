let nextActivityId = 10;
let nextFriendshipId = 10;

export const currentUser = {
  id: 1,
  username: "alex_runner",
  bio: "Trail runner & weekend cyclist. Chasing PRs and sunrises.",
  location: "Portland, OR",
  created_at: "2024-11-01T08:00:00Z",
};

export const users = [
  currentUser,
  { id: 2, username: "maria_rides", bio: "Cycling through life", location: "Denver, CO", created_at: "2024-10-15T10:00:00Z" },
  { id: 3, username: "sam_swims", bio: "Lap by lap", location: "Austin, TX", created_at: "2024-12-01T12:00:00Z" },
  { id: 4, username: "jordan_peaks", bio: "If it's uphill, I'm in", location: "Boulder, CO", created_at: "2025-01-10T09:00:00Z" },
  { id: 5, username: "casey_runs", bio: "Marathon addict. 26.2 or bust.", location: "Seattle, WA", created_at: "2025-02-05T11:00:00Z" },
  { id: 6, username: "taylor_trails", bio: null, location: "Bend, OR", created_at: "2025-03-12T14:00:00Z" },
  { id: 7, username: "riley_watts", bio: "Spin class warrior", location: "San Francisco, CA", created_at: "2025-01-20T08:00:00Z" },
  { id: 8, username: "quinn_strides", bio: "Walking is underrated", location: "Portland, OR", created_at: "2025-04-01T10:00:00Z" },
];

const userMap = Object.fromEntries(users.map((u) => [u.id, u.username]));

export function enrichActivity(a) {
  return { ...a, owner_username: userMap[a.owner_id] ?? "unknown" };
}

export let friendships = [
  { id: 1, requester_id: 1, addressee_id: 2, status: "accepted", created_at: "2025-01-01T00:00:00Z" },
  { id: 2, requester_id: 1, addressee_id: 3, status: "accepted", created_at: "2025-01-15T00:00:00Z" },
  { id: 3, requester_id: 4, addressee_id: 1, status: "accepted", created_at: "2025-02-01T00:00:00Z" },
  { id: 4, requester_id: 5, addressee_id: 1, status: "pending", created_at: "2025-05-10T00:00:00Z" },
  { id: 5, requester_id: 8, addressee_id: 1, status: "pending", created_at: "2025-05-11T00:00:00Z" },
  { id: 6, requester_id: 2, addressee_id: 3, status: "accepted", created_at: "2025-01-20T00:00:00Z" },
];

export function getFriendsOf(userId) {
  return friendships
    .filter((f) => f.status === "accepted" && (f.requester_id === userId || f.addressee_id === userId))
    .map((f) => (f.requester_id === userId ? f.addressee_id : f.requester_id));
}

export function getPendingRequestsFor(userId) {
  return friendships.filter((f) => f.status === "pending" && f.addressee_id === userId);
}

// Polylines (small Portland-area routes encoded with @mapbox/polyline)
const POLYLINES = {
  forest_park: "yvotGxwrkVm@gAcAkBq@yAiA_CgAgCe@aBMkA?eALgAd@mAv@gAhAeAfA_@|@IpAHpAb@lA|@hAdAbAjAh@jANfA",
  waterfront: "k`ptGhaqkV?iE?_F?{D?mE?oC?gD?aC?gBBqDDuBHiB",
  tabor: "s}otG~lpkVkAyA{@oAg@iAOwAJuAb@sAv@iAbA{@hAs@jBgAfCeA",
  hawthorne: "u|otGrkpkV?_D?sC?mB?eD?{B?qC?uB?gC",
};

export let activities = [
  {
    id: 1, owner_id: 1, title: "Morning trail run — Forest Park",
    sport_type: "run", distance: 8500, duration: 2700, elevation: 210,
    polyline: POLYLINES.forest_park, visibility: "public",
    started_at: "2025-05-12T06:30:00Z", created_at: "2025-05-12T07:15:00Z",
    kudos_count: 3, tagged_athlete_ids: [4],
  },
  {
    id: 2, owner_id: 2, title: "Weekend century ride",
    sport_type: "ride", distance: 162000, duration: 18000, elevation: 1450,
    polyline: POLYLINES.hawthorne, visibility: "public",
    started_at: "2025-05-11T07:00:00Z", created_at: "2025-05-11T12:00:00Z",
    kudos_count: 12, tagged_athlete_ids: [],
  },
  {
    id: 3, owner_id: 3, title: "Pool laps",
    sport_type: "swim", distance: 2000, duration: 2400, elevation: null,
    polyline: null, visibility: "friends",
    started_at: "2025-05-10T17:00:00Z", created_at: "2025-05-10T17:40:00Z",
    kudos_count: 1, tagged_athlete_ids: [],
  },
  {
    id: 4, owner_id: 1, title: "Easy recovery jog",
    sport_type: "run", distance: 5000, duration: 1800, elevation: 30,
    polyline: POLYLINES.waterfront, visibility: "public",
    started_at: "2025-05-09T07:00:00Z", created_at: "2025-05-09T07:30:00Z",
    kudos_count: 0, tagged_athlete_ids: [],
  },
  {
    id: 5, owner_id: 2, title: "Lunch walk",
    sport_type: "walk", distance: 3200, duration: 2400, elevation: 15,
    polyline: null, visibility: "public",
    started_at: "2025-05-08T12:00:00Z", created_at: "2025-05-08T12:40:00Z",
    kudos_count: 2, tagged_athlete_ids: [3],
  },
  {
    id: 6, owner_id: 1, title: "Mt. Tabor hike",
    sport_type: "hike", distance: 14000, duration: 14400, elevation: 890,
    polyline: POLYLINES.tabor, visibility: "friends",
    started_at: "2025-05-06T08:00:00Z", created_at: "2025-05-06T12:00:00Z",
    kudos_count: 7, tagged_athlete_ids: [2, 4],
  },
  {
    id: 7, owner_id: 4, title: "Sunrise summit push",
    sport_type: "hike", distance: 11000, duration: 10800, elevation: 720,
    polyline: POLYLINES.tabor, visibility: "public",
    started_at: "2025-05-05T05:00:00Z", created_at: "2025-05-05T08:00:00Z",
    kudos_count: 9, tagged_athlete_ids: [1],
  },
  {
    id: 8, owner_id: 5, title: "Tempo 10K",
    sport_type: "run", distance: 10000, duration: 2520, elevation: 45,
    polyline: POLYLINES.waterfront, visibility: "public",
    started_at: "2025-05-04T07:00:00Z", created_at: "2025-05-04T07:42:00Z",
    kudos_count: 5, tagged_athlete_ids: [],
  },
  {
    id: 9, owner_id: 7, title: "Evening spin",
    sport_type: "ride", distance: 25000, duration: 3600, elevation: 120,
    polyline: POLYLINES.hawthorne, visibility: "public",
    started_at: "2025-05-03T18:00:00Z", created_at: "2025-05-03T19:00:00Z",
    kudos_count: 3, tagged_athlete_ids: [],
  },
];

export const segments = [
  {
    id: 1, name: "Forest Park Firelane 1 Climb", polyline: POLYLINES.forest_park,
    distance: 2100, sport_type: "run",
  },
  {
    id: 2, name: "Waterfront Sprint", polyline: POLYLINES.waterfront,
    distance: 1600, sport_type: "run",
  },
  {
    id: 3, name: "Tabor Summit Loop", polyline: POLYLINES.tabor,
    distance: 3200, sport_type: "hike",
  },
  {
    id: 4, name: "Hawthorne Bridge Dash", polyline: POLYLINES.hawthorne,
    distance: 800, sport_type: "ride",
  },
];

export const segmentEfforts = [
  { id: 1, segment_id: 1, activity_id: 1, athlete_id: 1, elapsed_time: 612, started_at: "2025-05-12T06:40:00Z" },
  { id: 2, segment_id: 1, activity_id: 7, athlete_id: 4, elapsed_time: 588, started_at: "2025-05-05T05:20:00Z" },
  { id: 3, segment_id: 1, activity_id: 8, athlete_id: 5, elapsed_time: 540, started_at: "2025-05-04T07:10:00Z" },
  { id: 4, segment_id: 2, activity_id: 4, athlete_id: 1, elapsed_time: 378, started_at: "2025-05-09T07:08:00Z" },
  { id: 5, segment_id: 2, activity_id: 8, athlete_id: 5, elapsed_time: 352, started_at: "2025-05-04T07:15:00Z" },
  { id: 6, segment_id: 2, activity_id: 1, athlete_id: 1, elapsed_time: 390, started_at: "2025-05-12T06:45:00Z" },
  { id: 7, segment_id: 3, activity_id: 6, athlete_id: 1, elapsed_time: 1020, started_at: "2025-05-06T08:30:00Z" },
  { id: 8, segment_id: 3, activity_id: 7, athlete_id: 4, elapsed_time: 960, started_at: "2025-05-05T05:45:00Z" },
  { id: 9, segment_id: 4, activity_id: 2, athlete_id: 2, elapsed_time: 95, started_at: "2025-05-11T08:00:00Z" },
  { id: 10, segment_id: 4, activity_id: 9, athlete_id: 7, elapsed_time: 102, started_at: "2025-05-03T18:20:00Z" },
];

export const stats = {
  totals: {
    run: { count: 2, total_distance: 13500, total_elevation: 240 },
    ride: { count: 0, total_distance: 0, total_elevation: 0 },
    swim: { count: 0, total_distance: 0, total_elevation: null },
    walk: { count: 0, total_distance: 0, total_elevation: 0 },
    hike: { count: 1, total_distance: 14000, total_elevation: 890 },
  },
  personal_records: {
    fastest_5k: 1500,
    fastest_10k: 3180,
    longest_run: 8500,
    biggest_climb: 890,
  },
};

export function createActivity(data) {
  const activity = {
    id: nextActivityId++,
    owner_id: currentUser.id,
    ...data,
    created_at: new Date().toISOString(),
    kudos_count: 0,
    tagged_athlete_ids: data.tagged_athlete_ids ?? [],
  };
  activities.unshift(activity);
  return enrichActivity(activity);
}

export function addFriendship(requesterId, addresseeId) {
  const existing = friendships.find(
    (f) =>
      (f.requester_id === requesterId && f.addressee_id === addresseeId) ||
      (f.requester_id === addresseeId && f.addressee_id === requesterId),
  );
  if (existing) return existing;
  const f = { id: nextFriendshipId++, requester_id: requesterId, addressee_id: addresseeId, status: "pending", created_at: new Date().toISOString() };
  friendships.push(f);
  return f;
}

export function acceptFriendship(requesterId, addresseeId) {
  const f = friendships.find((f) => f.requester_id === requesterId && f.addressee_id === addresseeId && f.status === "pending");
  if (f) f.status = "accepted";
  return f;
}
