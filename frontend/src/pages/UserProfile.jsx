import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getUser, getUserActivities, followUser, acceptFollow, unfollowUser, getFollowing, getSentRequests, getPendingRequests } from "../api/users";
import ActivityCard from "../components/ActivityCard";
import ActivityFilters from "../components/ActivityFilters";
import SportIcon from "../components/SportIcon";
import { useAuth } from "../context/AuthContext";
import { HERO_IMAGES, EMPTY_STATE_IMAGES } from "../constants/images";

const AVATAR_COLORS = [
  "#fc4c02", "#16a34a", "#0284c7", "#9333ea", "#e11d48",
  "#0d9488", "#a16207", "#6d28d9",
];

function avatarColor(id) {
  return AVATAR_COLORS[id % AVATAR_COLORS.length];
}

const SPORT_LABELS = {
  run: "Running",
  ride: "Cycling",
  walk: "Walking",
  hike: "Hiking",
};

const SPORT_COLORS = {
  run: "var(--sport-run)",
  ride: "var(--sport-ride)",
  walk: "var(--sport-walk)",
  hike: "var(--sport-hike)",
};

export default function UserProfile() {
  const { id: userId } = useParams();
  const { user: currentUser } = useAuth();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [sportFilter, setSportFilter] = useState("all");

  const { data: profileUser, isLoading: userLoading, isError: userError } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => getUser(userId),
  });

  const { data: activities, isLoading: actLoading } = useQuery({
    queryKey: ["userActivities", userId],
    queryFn: () => getUserActivities(userId, { limit: 50 }),
  });

  const { data: following } = useQuery({
    queryKey: ["following"],
    queryFn: getFollowing,
  });

  const { data: sentRequests } = useQuery({
    queryKey: ["sentRequests"],
    queryFn: getSentRequests,
  });

  const { data: pendingRequests } = useQuery({
    queryKey: ["pendingRequests"],
    queryFn: getPendingRequests,
  });

  const followingIds = new Set((following ?? []).map((u) => u.id));
  const pendingOutgoingIds = new Set((sentRequests ?? []).map((r) => r.addressee_id));
  const pendingIncomingIds = new Set((pendingRequests ?? []).map((r) => r.requester_id));

  const followMutation = useMutation({
    mutationFn: followUser,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["following"] });
      qc.invalidateQueries({ queryKey: ["sentRequests"] });
      qc.invalidateQueries({ queryKey: ["searchUsers"] });
    },
  });

  const unfollowMutation = useMutation({
    mutationFn: unfollowUser,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["following"] });
      qc.invalidateQueries({ queryKey: ["searchUsers"] });
    },
  });

  const acceptMutation = useMutation({
    mutationFn: acceptFollow,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["following"] });
      qc.invalidateQueries({ queryKey: ["pendingRequests"] });
      qc.invalidateQueries({ queryKey: ["sentRequests"] });
    },
  });

  if (userLoading) return <div className="page"><div className="skeleton" style={{ height: 200 }} /></div>;
  if (userError || !profileUser) return <div className="page"><div className="error">User not found.</div></div>;

  if (currentUser && String(profileUser.id) === String(currentUser.id)) {
    navigate("/profile", { replace: true });
    return null;
  }

  const isSelf = currentUser && String(profileUser.id) === String(currentUser.id);
  let followStatus = null;
  if (!isSelf) {
    if (followingIds.has(profileUser.id)) followStatus = "accepted";
    else if (pendingIncomingIds.has(profileUser.id)) followStatus = "incoming";
    else if (pendingOutgoingIds.has(profileUser.id)) followStatus = "pending";
  }

  let actionBtn = null;
  if (followStatus === "accepted") {
    actionBtn = <button className="btn-ghost btn-sm follow-btn follow-btn-following" onClick={() => unfollowMutation.mutate(profileUser.id)} disabled={unfollowMutation.isPending}>Following</button>;
  } else if (followStatus === "pending") {
    actionBtn = <button className="btn-sm follow-btn follow-btn-pending" disabled>Pending</button>;
  } else if (followStatus === "incoming") {
    actionBtn = <button className="btn-primary btn-sm follow-btn" onClick={() => acceptMutation.mutate(profileUser.id)} disabled={acceptMutation.isPending}>Accept</button>;
  } else if (followStatus === null && !isSelf) {
    actionBtn = <button className="btn-primary btn-sm follow-btn" onClick={() => followMutation.mutate(profileUser.id)} disabled={followMutation.isPending}>Follow</button>;
  }

  const filtered = sportFilter === "all"
    ? (activities ?? [])
    : (activities ?? []).filter((a) => a.sport_type === sportFilter);

  const sportTotals = {};
  for (const a of activities ?? []) {
    const s = a.sport_type;
    if (!sportTotals[s]) sportTotals[s] = { count: 0, total_distance: 0, total_elevation: 0 };
    sportTotals[s].count += 1;
    sportTotals[s].total_distance += a.distance ?? 0;
    sportTotals[s].total_elevation += a.elevation ?? 0;
  }
  const sportTotalEntries = Object.entries(sportTotals).filter(([, v]) => v.count > 0);

  return (
    <div className="page">
      <div className="card-flush" style={{ marginBottom: 20 }}>
        <div className="profile-cover" style={{ backgroundImage: `url(${HERO_IMAGES.profile})` }}>
          <div className="profile-cover-overlay" />
        </div>
        <div className="profile-hero">
          <div className="avatar avatar-xl profile-avatar" style={{ background: avatarColor(profileUser.id) }}>
            {profileUser.username[0].toUpperCase()}
          </div>
          <div className="profile-info">
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <h2>{profileUser.username}</h2>
              {actionBtn}
            </div>
            {profileUser.location && <p className="profile-location">{profileUser.location}</p>}
            {profileUser.bio && <p className="profile-bio">{profileUser.bio}</p>}
            <p className="profile-joined">
              Joined {new Date(profileUser.created_at).toLocaleDateString("en-US", { month: "long", year: "numeric" })}
            </p>
          </div>
        </div>
      </div>

      {sportTotalEntries.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 className="section-title">Training Totals</h3>
          <div className="stats-grid">
            {sportTotalEntries.map(([sport, data]) => {
              const label = SPORT_LABELS[sport] ?? sport;
              return (
                <div className="stat" key={sport}>
                  <div className="stat-sport-icon" style={{ color: SPORT_COLORS[sport] }}>
                    <SportIcon sport={sport} size={28} color="currentColor" />
                  </div>
                  <div className="stat-value">{data.count}</div>
                  <div className="stat-label">{label}</div>
                  <div style={{ marginTop: 8, fontSize: "0.75rem", color: "var(--text-muted)" }}>
                    {(data.total_distance / 1000).toFixed(1)} km
                    {data.total_elevation > 0 && <> · {data.total_elevation.toFixed(0)}m elev</>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <h3 className="section-title">Activities</h3>
      <ActivityFilters selected={sportFilter} onChange={setSportFilter} />

      {filtered.length === 0 && (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-image">
              <img src={EMPTY_STATE_IMAGES.noActivities} alt="No activities" />
            </div>
            <h3>No activities</h3>
            <p>{sportFilter === "all" ? "This user hasn't logged any activities yet." : `No ${sportFilter} activities yet.`}</p>
          </div>
        </div>
      )}
      {filtered.map((a, i) => (
        <ActivityCard
          key={a.id}
          activity={a}
          queryKey={["userActivities", userId]}
          style={{ animationDelay: `${Math.min(i, 5) * 60}ms` }}
        />
      ))}
    </div>
  );
}