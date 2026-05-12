import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getSegments } from "../api/segments";

const SPORT_EMOJI = { run: "\u{1F3C3}", ride: "\u{1F6B4}", swim: "\u{1F3CA}", walk: "\u{1F6B6}", hike: "\u{1F97E}" };

function fmt(seconds) {
  if (!seconds) return "—";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function Segments() {
  const { data: segments, isLoading } = useQuery({
    queryKey: ["segments"],
    queryFn: getSegments,
  });

  return (
    <div className="page">
      <h2 className="section-title" style={{ marginBottom: 24, fontSize: "var(--text-2xl)" }}>
        Segments
      </h2>

      {isLoading && (
        <div className="segment-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton" style={{ height: 120, borderRadius: "var(--radius-lg)" }} />
          ))}
        </div>
      )}

      <div className="segment-grid">
        {segments?.map((seg) => (
          <Link to={`/segments/${seg.id}`} key={seg.id} style={{ textDecoration: "none" }}>
            <div className="segment-card">
              <div className="segment-card-name">
                {SPORT_EMOJI[seg.sport_type] ?? ""} {seg.name}
              </div>
              <div className="segment-card-meta">
                <span className={`badge badge-${seg.sport_type}`}>{seg.sport_type}</span>
                <span>{(seg.distance / 1000).toFixed(2)} km</span>
                {seg.my_best_time && (
                  <span style={{ color: "var(--accent)", fontWeight: 700 }}>
                    PR: {fmt(seg.my_best_time)}
                  </span>
                )}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
