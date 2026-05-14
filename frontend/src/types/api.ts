// Shared API/domain types matching the FastAPI backend schemas.

export type SportType = "run" | "ride" | "walk" | "hike";
export type Visibility = "public" | "friends" | "private";

export interface User {
  id: number;
  username: string;
  bio?: string | null;
  location?: string | null;
  created_at: string;
  email?: string;
}

export interface Activity {
  id: number;
  owner_id: number;
  owner_username?: string | null;
  title: string;
  sport_type: SportType;
  distance: number | null;
  duration: number | null;
  elevation: number | null;
  polyline: string | null;
  visibility: Visibility;
  started_at: string | null;
  created_at: string;
  kudos_count: number;
  user_has_kudos: boolean;
  tagged_athlete_ids?: number[];
}

export interface ActivityCreatePayload {
  title: string;
  sport_type: SportType;
  distance?: number | null;
  duration?: number | null;
  elevation?: number | null;
  polyline?: string | null;
  visibility?: Visibility;
  started_at?: string | null;
  tagged_athlete_ids?: number[];
}

export interface ActivityUpdatePayload extends Partial<ActivityCreatePayload> {}

export interface Segment {
  id: number;
  name: string;
  polyline: string | null;
  distance: number | null;
  sport_type?: SportType;
}

export interface SegmentCreatePayload {
  name: string;
  distance?: number | null;
  polyline?: string | null;
}

export interface LeaderboardEntry {
  athlete_id: number;
  athlete_name: string;
  best_time: number;
  rank: number;
}

export interface FriendRequest {
  id: number;
  requester_id: number;
  addressee_id: number;
  requester?: User;
  status: "pending" | "accepted";
  created_at: string;
}

export interface SportTotals {
  count: number;
  total_distance: number;
  total_elevation: number | null;
  total_duration: number;
}

export interface PersonalRecord {
  segment_id: number;
  best_time: number;
}

export interface Stats {
  totals: Record<SportType, SportTotals>;
  personal_records: PersonalRecord[];
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string | null;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}
