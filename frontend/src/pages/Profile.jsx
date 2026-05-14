import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getStats, getUserActivities } from "../api/users";
import ActivityCard from "../components/ActivityCard";
import ActivityFilters from "../components/ActivityFilters";
import EditProfileModal from "../components/EditProfileModal";
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

function fmtTime(seconds) {
  if (seconds == null) return "—";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function Profile() {
  const { user } = useAuth();
  const [editing, setEditing] = useState(false);
  const [sportFilter, setSportFilter] = useState("all");

  const { data: stats } = useQuery({ queryKey: ["stats"], queryFn: getStats, enabled: !!user });

  const { data: activities } = useQuery({
    queryKey: ["myActivities"],
    queryFn: () => getUserActivities(user.id, { limit: 50 }),
    enabled: !!user,
  });

  const myActivities = activities ?? [];
  const filtered = sportFilter === "all"
    ? myActivities
    : myActivities.filter((a) => a.sport_type === sportFilter);

  const sportTotals = stats?.totals
    ? Object.entries(stats.totals).filter(([, v]) => v.count > 0)
    : [];

  const prs = Array.isArray(stats?.personal_records)
    ? stats.personal_records.filter((pr) => pr?.best_time != null)
    : [];

  return (
    <div className="page">
      {editing && <EditProfileModal onClose={() => setEditing(false)} />}

      <div className="card-flush profile-card" style={{ backgroundImage: `url(${HERO_IMAGES.profile})`, marginBottom: 20 }}>
        <div className="profile-cover-overlay" />
        <div className="profile-hero">
          <div className="avatar avatar-xl profile-avatar" style={{ background: avatarColor(user?.id ?? 0) }}>
            {user?.username?.[0]?.toUpperCase()}
          </div>
          <div className="profile-info">
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <h2>{user?.username}</h2>
              <button className="edit-btn" onClick={() => setEditing(true)}>Edit</button>
            </div>
            {user?.location && <p className="profile-location">{user.location}</p>}
            {user?.bio && <p className="profile-bio">{user.bio}</p>}
            <p className="profile-joined">
              Joined {new Date(user?.created_at).toLocaleDateString("en-US", { month: "long", year: "numeric" })}
            </p>
          </div>
        </div>
      </div>

      {prs.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 className="section-title">Personal Records</h3>
          <div className="pr-grid">
            {prs.map((pr) => (
              <div className="pr-card" key={pr.segment_id}>
                <div className="pr-card-value">{fmtTime(pr.best_time)}</div>
                <div className="pr-card-label">Segment #{pr.segment_id}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {sportTotals.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 className="section-title">Training Totals</h3>
          <div className="stats-grid">
            {sportTotals.map(([sport, data]) => {
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
                    {data.total_elevation != null && data.total_elevation > 0 && (
                      <> · {data.total_elevation.toFixed(0)}m elev</>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <h3 className="section-title">Recent Activities</h3>
      <ActivityFilters selected={sportFilter} onChange={setSportFilter} />

      {filtered.length === 0 && (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-image">
              <img src={EMPTY_STATE_IMAGES.noActivities} alt="No activities" />
            </div>
            <h3>No activities</h3>
            <p>{sportFilter === "all" ? "Log your first activity to start tracking!" : `No ${sportFilter} activities yet.`}</p>
          </div>
        </div>
      )}
      {filtered.map((a, i) => (
        <ActivityCard
          key={a.id}
          activity={a}
          queryKey={["myActivities"]}
          style={{ animationDelay: `${Math.min(i, 5) * 60}ms` }}
        />
      ))}
    </div>
  );
}
