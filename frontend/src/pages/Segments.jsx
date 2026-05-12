import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getSegments } from "../api/segments";
import SportIcon from "../components/SportIcon";
import { SPORT_THUMBNAILS, HERO_IMAGES } from "../constants/images";

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
      <div className="segments-hero" style={{ backgroundImage: `url(${HERO_IMAGES.segments})` }}>
        <div className="segments-hero-overlay">
          <h2>Segments</h2>
          <p>Challenge yourself on popular routes</p>
        </div>
      </div>

      {isLoading && (
        <div className="segment-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton" style={{ height: 180, borderRadius: "var(--radius-lg)" }} />
          ))}
        </div>
      )}

      <div className="segment-grid">
        {segments?.map((seg) => (
          <Link to={`/segments/${seg.id}`} key={seg.id} style={{ textDecoration: "none" }}>
            <div className="segment-card segment-card-image">
              <div
                className="segment-card-bg"
                style={{ backgroundImage: `url(${SPORT_THUMBNAILS[seg.sport_type] ?? SPORT_THUMBNAILS.run})` }}
              />
              <div className="segment-card-content">
                <div className="segment-card-sport-icon">
                  <SportIcon sport={seg.sport_type} size={20} color="#fff" />
                </div>
                <div className="segment-card-name">{seg.name}</div>
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
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
