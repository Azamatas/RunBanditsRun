import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getSegment, getSegmentLeaderboard } from "../api/segments";
import MapView from "../components/MapView";
import LeaderboardTable from "../components/LeaderboardTable";

const SPORT_COLORS = {
  run: "var(--sport-run)", ride: "var(--sport-ride)", swim: "var(--sport-swim)",
  walk: "var(--sport-walk)", hike: "var(--sport-hike)",
};

export default function SegmentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: segment, isLoading } = useQuery({
    queryKey: ["segment", id],
    queryFn: () => getSegment(id),
  });

  const { data: leaderboard } = useQuery({
    queryKey: ["leaderboard", id],
    queryFn: () => getSegmentLeaderboard(id),
  });

  if (isLoading) {
    return (
      <div className="page">
        <div className="skeleton" style={{ height: 240, borderRadius: "var(--radius-lg)", marginBottom: 16 }} />
        <div className="skeleton" style={{ height: 300, borderRadius: "var(--radius-lg)" }} />
      </div>
    );
  }

  if (!segment) {
    return (
      <div className="page">
        <div className="error">Segment not found.</div>
      </div>
    );
  }

  return (
    <div className="page">
      <button className="btn-secondary" style={{ marginBottom: 16 }} onClick={() => navigate(-1)}>
        ← Back
      </button>

      <div className="card-flush" style={{ marginBottom: 24 }}>
        {segment.polyline && (
          <MapView
            polyline={segment.polyline}
            height={240}
            sportColor={SPORT_COLORS[segment.sport_type] ?? "var(--accent)"}
          />
        )}
        <div style={{ padding: 24 }}>
          <h1 style={{ fontSize: "var(--text-2xl)", fontWeight: 800, letterSpacing: "-0.03em" }}>
            {segment.name}
          </h1>
          <div style={{ display: "flex", gap: 16, marginTop: 12 }}>
            <span className={`badge badge-${segment.sport_type}`}>{segment.sport_type}</span>
            <span style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)" }}>
              {(segment.distance / 1000).toFixed(2)} km
            </span>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="section-title">Leaderboard</h3>
        <LeaderboardTable efforts={leaderboard} />
      </div>
    </div>
  );
}
