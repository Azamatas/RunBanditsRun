import { Link } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { giveKudos, removeKudos } from "../api/activities";
import { useAuth } from "../context/AuthContext";
import SportIcon, { KudosIcon } from "./SportIcon";
import { SPORT_THUMBNAILS } from "../constants/images";

const AVATAR_COLORS = [
  "#fc4c02", "#16a34a", "#0284c7", "#9333ea", "#e11d48",
  "#0d9488", "#a16207", "#6d28d9",
];

function avatarColor(id) {
  return AVATAR_COLORS[id % AVATAR_COLORS.length];
}

function fmt(seconds) {
  if (!seconds) return "—";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return h > 0 ? `${h}h ${m}m` : `${m}m ${String(s).padStart(2, "0")}s`;
}

function timeAgo(dateStr) {
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return new Date(dateStr).toLocaleDateString();
}

export default function ActivityCard({ activity, queryKey, style }) {
  const { user } = useAuth();
  const qc = useQueryClient();

  const kudosMutation = useMutation({
    mutationFn: () => giveKudos(activity.id),
    onSuccess: () => qc.invalidateQueries({ queryKey }),
  });

  const isOwner = user?.id === activity.owner_id;
  const username = activity.owner_username ?? "athlete";
  const pace =
    activity.distance && activity.duration
      ? fmt(Math.round(activity.duration / (activity.distance / 1000)))
      : null;

  return (
    <div className="activity-card" style={style}>
      <div
        className="activity-card-image"
        style={{ backgroundImage: `url(${SPORT_THUMBNAILS[activity.sport_type] ?? SPORT_THUMBNAILS.run})` }}
      >
        <div className="activity-card-image-overlay">
          <span className={`badge badge-${activity.sport_type} badge-on-image`}>
            <SportIcon sport={activity.sport_type} size={14} color="currentColor" />
            {activity.sport_type}
          </span>
        </div>
      </div>

      <div className="activity-card-body">
        <div className="activity-card-header">
          <div className="avatar avatar-sm" style={{ background: avatarColor(activity.owner_id) }}>
            {username[0].toUpperCase()}
          </div>
          <div className="activity-card-user">
            <span className="activity-card-username">{username}</span>
            <span className="activity-card-meta">
              <span>{timeAgo(activity.created_at)}</span>
            </span>
          </div>
        </div>

        <Link to={`/activities/${activity.id}`} className="activity-card-title">
          {activity.title}
        </Link>

        <div className="activity-card-stats">
          {activity.distance != null && (
            <div className="stat-inline">
              <span className="stat-value">{(activity.distance / 1000).toFixed(2)}</span>
              <span className="stat-label">km</span>
            </div>
          )}
          {activity.duration != null && (
            <div className="stat-inline">
              <span className="stat-value">{fmt(activity.duration)}</span>
              <span className="stat-label">time</span>
            </div>
          )}
          {activity.elevation != null && (
            <div className="stat-inline">
              <span className="stat-value">{activity.elevation}</span>
              <span className="stat-label">m elev</span>
            </div>
          )}
          {pace && (
            <div className="stat-inline">
              <span className="stat-value">{pace}</span>
              <span className="stat-label">/km</span>
            </div>
          )}
        </div>

        <div className="activity-card-footer">
          {!isOwner ? (
            <button
              className={`kudos-btn${kudosMutation.isSuccess ? " active" : ""}`}
              onClick={() => kudosMutation.mutate()}
              disabled={kudosMutation.isPending}
            >
              <KudosIcon size={16} color="currentColor" />
              <span>Kudos</span>
              <span>({activity.kudos_count})</span>
            </button>
          ) : (
            <span className="kudos-btn active" style={{ cursor: "default" }}>
              <KudosIcon size={16} color="currentColor" />
              <span>{activity.kudos_count} kudos</span>
            </span>
          )}

          {activity.visibility !== "public" && (
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "capitalize" }}>
              {activity.visibility}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
