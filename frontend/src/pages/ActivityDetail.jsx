import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getActivity, deleteActivity, giveKudos, removeKudos } from "../api/activities";
import { useAuth } from "../context/AuthContext";
import MapView from "../components/MapView";
import SportIcon, { KudosIcon } from "../components/SportIcon";
import { SPORT_IMAGES } from "../constants/images";

const SPORT_COLORS = {
  run: "var(--sport-run)", ride: "var(--sport-ride)",
  walk: "var(--sport-walk)", hike: "var(--sport-hike)",
};
const AVATAR_COLORS = ["#fc4c02", "#16a34a", "#0284c7", "#9333ea", "#e11d48", "#0d9488", "#a16207", "#6d28d9"];

function fmt(seconds) {
  if (!seconds) return "—";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return h > 0 ? `${h}h ${m}m` : `${m}m ${String(s).padStart(2, "0")}s`;
}

export default function ActivityDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data: activity, isLoading, isError } = useQuery({
    queryKey: ["activity", id],
    queryFn: () => getActivity(id),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteActivity(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["feed"] }); navigate("/feed"); },
  });

  const hasKudos = activity?.user_has_kudos ?? false;

  const kudosMutation = useMutation({
    mutationFn: () => hasKudos ? removeKudos(id) : giveKudos(id),
    onMutate: async () => {
      await qc.cancelQueries({ queryKey: ["activity", id] });
      const prev = qc.getQueryData(["activity", id]);
      qc.setQueryData(["activity", id], (old) => {
        if (!old) return old;
        return { ...old, user_has_kudos: !hasKudos, kudos_count: hasKudos ? old.kudos_count - 1 : old.kudos_count + 1 };
      });
      return { prev };
    },
    onError: (err, vars, context) => {
      if (context?.prev) qc.setQueryData(["activity", id], context.prev);
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["activity", id] });
    },
  });

  if (isLoading) {
    return (
      <div className="page">
        <div className="skeleton" style={{ height: 300, borderRadius: "var(--radius-lg)" }} />
      </div>
    );
  }

  if (isError || !activity) {
    return (
      <div className="page">
        <div className="error">Activity not found.</div>
        <button className="btn-secondary" onClick={() => navigate("/feed")} style={{ marginTop: 12 }}>Back to Feed</button>
      </div>
    );
  }

  const isOwner = user?.id === activity.owner_id;
  const pace = activity.distance && activity.duration
    ? fmt(Math.round(activity.duration / (activity.distance / 1000)))
    : null;
  const sportType = activity.sport_type;
  const taggedIds = activity.tagged_athlete_ids ?? [];
  const hasMap = !!activity.polyline;

  return (
    <div className="page">
      <button className="btn-secondary" style={{ marginBottom: 16 }} onClick={() => navigate(-1)}>
        ← Back
      </button>

      <div className="card-flush">
        {hasMap ? (
          <MapView polyline={activity.polyline} height={280} sportColor={SPORT_COLORS[sportType]} />
        ) : (
          <div
            className="detail-hero-image"
            style={{ backgroundImage: `url(${SPORT_IMAGES[sportType] ?? SPORT_IMAGES.run})` }}
          >
            <div className="detail-hero-image-overlay" />
          </div>
        )}

        <div className={`detail-header detail-header-${sportType}`}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div>
              <span className="badge badge-on-image" style={{ background: "rgba(255,255,255,0.2)", color: "#fff", marginBottom: 8 }}>
                <SportIcon sport={sportType} size={14} color="#fff" />
                {sportType}
              </span>
              <h1 style={{ fontSize: "1.75rem", fontWeight: 800, letterSpacing: "-0.03em", marginTop: 8 }}>
                {activity.title}
              </h1>
              <p style={{ opacity: 0.85, fontSize: "0.8125rem", marginTop: 4 }}>
                <Link to={`/users/${activity.owner_id}`} style={{ color: "#fff" }}>
                  {activity.owner_username ?? "athlete"}
                </Link>
                {" · "}
                {new Date(activity.created_at).toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" })}
              </p>
            </div>
            {isOwner && (
              <div style={{ display: "flex", gap: 8 }}>
                <Link
                  to={`/activities/${id}/edit`}
                  className="edit-btn"
                  style={{ background: "rgba(255,255,255,0.15)", color: "#fff" }}
                >
                  Edit
                </Link>
                <button
                  className="btn-danger"
                  style={{ background: "rgba(255,255,255,0.15)", color: "#fff", borderColor: "rgba(255,255,255,0.3)" }}
                  onClick={() => { if (confirm("Delete this activity?")) deleteMutation.mutate(); }}
                >
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="detail-stats">
          {activity.distance != null && (
            <div className="detail-stat">
              <div className="detail-stat-value">{(activity.distance / 1000).toFixed(2)}</div>
              <div className="detail-stat-label">Kilometers</div>
            </div>
          )}
          {activity.duration != null && (
            <div className="detail-stat">
              <div className="detail-stat-value">{fmt(activity.duration)}</div>
              <div className="detail-stat-label">Duration</div>
            </div>
          )}
          {pace && (
            <div className="detail-stat">
              <div className="detail-stat-value">{pace}</div>
              <div className="detail-stat-label">Pace /km</div>
            </div>
          )}
          {activity.elevation != null && (
            <div className="detail-stat">
              <div className="detail-stat-value">{activity.elevation}</div>
              <div className="detail-stat-label">Elevation (m)</div>
            </div>
          )}
        </div>

        {taggedIds.length > 0 && (
          <div className="tagged-row" style={{ padding: "0 24px 16px", borderTop: "none" }}>
            {taggedIds.map((tid) => (
              <div
                key={tid}
                className="avatar avatar-sm"
                style={{ background: AVATAR_COLORS[tid % AVATAR_COLORS.length] }}
                title={`Athlete #${tid}`}
              >
                {String.fromCharCode(65 + (tid % 26))}
              </div>
            ))}
            <span style={{ marginLeft: 8 }}>
              {taggedIds.length} tagged athlete{taggedIds.length !== 1 ? "s" : ""}
            </span>
          </div>
        )}

        <div style={{ padding: "16px 24px", borderTop: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 16 }}>
          {!isOwner ? (
            <button
              className={`kudos-btn${hasKudos ? " active" : ""}`}
              onClick={() => kudosMutation.mutate()}
              disabled={kudosMutation.isPending}
            >
              <KudosIcon size={16} color="currentColor" />
              {hasKudos ? "Kudos Given" : "Give Kudos"} ({activity.kudos_count})
            </button>
          ) : (
            <span className="kudos-btn active" style={{ cursor: "default" }}>
              <KudosIcon size={16} color="currentColor" />
              {activity.kudos_count} kudos
            </span>
          )}
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "capitalize", marginLeft: "auto" }}>
            {activity.visibility}
          </span>
        </div>
      </div>
    </div>
  );
}
