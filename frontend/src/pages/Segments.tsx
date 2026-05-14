import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { MapContainer, TileLayer, Polyline, useMap } from "react-leaflet";
import polylineCodec from "@mapbox/polyline";
import "leaflet/dist/leaflet.css";
import { getSegments, getSegmentLeaderboard } from "../api/segments";

const PALETTE = ["#fc4c02", "#0284c7", "#16a34a", "#9333ea", "#e11d48", "#0d9488", "#a16207", "#6d28d9"];

function segColor(i) {
  return PALETTE[i % PALETTE.length];
}

function fmt(seconds) {
  if (!seconds) return "—";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function decode(polyline) {
  try { return polylineCodec.decode(polyline); } catch { return []; }
}

function FitAll({ positions }) {
  const map = useMap();
  const key = positions.length;
  useEffect(() => {
    if (key > 0) map.fitBounds(positions, { padding: [40, 40] });
  }, [map, key]); // eslint-disable-line react-hooks/exhaustive-deps
  return null;
}

function FlyToSegment({ decoded, selectedId }) {
  const map = useMap();
  useEffect(() => {
    if (!selectedId) return;
    const target = decoded.find((d) => d.seg.id === selectedId);
    if (target?.positions?.length >= 2) {
      map.flyToBounds(target.positions, { padding: [60, 60], duration: 0.8 });
    }
  }, [selectedId]); // eslint-disable-line react-hooks/exhaustive-deps
  return null;
}

function SegmentCard({ seg, color, selected, onSelect, cardRef }) {
  const { data: leaderboard } = useQuery({
    queryKey: ["leaderboard", seg.id],
    queryFn: () => getSegmentLeaderboard(seg.id),
  });

  const top3 = leaderboard?.slice(0, 3) ?? [];

  return (
    <div
      ref={cardRef}
      onClick={() => onSelect(seg.id)}
      style={{
        background: "var(--bg-card)",
        border: `1.5px solid ${selected ? color : "var(--border)"}`,
        borderRadius: "var(--radius-lg)",
        overflow: "hidden",
        cursor: "pointer",
        boxShadow: selected ? `0 0 0 3px ${color}22` : "var(--shadow-sm)",
        transition: "box-shadow 0.2s, border-color 0.2s",
      }}
    >
      {/* Color bar + header */}
      <div style={{ borderLeft: `5px solid ${color}`, padding: "16px 20px 12px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
          <Link
            to={`/segments/${seg.id}`}
            onClick={(e) => e.stopPropagation()}
            style={{ fontWeight: 700, fontSize: "var(--text-base)", color: "var(--text)" }}
          >
            {seg.name}
          </Link>
          {seg.distance != null && (
            <span style={{ fontSize: "var(--text-sm)", color: "var(--text-muted)", whiteSpace: "nowrap" }}>
              {(seg.distance / 1000).toFixed(2)} km
            </span>
          )}
        </div>
      </div>

      {/* Leaderboard top 3 */}
      <div style={{ borderTop: "1px solid var(--gray-100)" }}>
        {top3.length === 0 ? (
          <p style={{ padding: "10px 20px", fontSize: "var(--text-xs)", color: "var(--text-muted)" }}>
            No efforts yet
          </p>
        ) : (
          top3.map((entry) => (
            <div
              key={entry.athlete_id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "8px 20px",
                borderBottom: "1px solid var(--gray-100)",
                fontSize: "var(--text-sm)",
              }}
            >
              <span style={{
                width: 20, height: 20, borderRadius: "50%",
                background: entry.rank === 1 ? "#fef08a" : entry.rank === 2 ? "#e5e7eb" : "#fed7aa",
                color: entry.rank === 1 ? "#a16207" : entry.rank === 2 ? "#6b7280" : "#c2410c",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "0.65rem", fontWeight: 800, flexShrink: 0,
              }}>
                {entry.rank}
              </span>
              <span style={{ flex: 1, fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {entry.athlete_name}
              </span>
              <span style={{ fontWeight: 700, fontVariantNumeric: "tabular-nums", color: "var(--text)" }}>
                {fmt(entry.best_time)}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default function Segments() {
  const [selectedId, setSelectedId] = useState(null);
  const cardRefs = useRef({});

  const { data: segments = [], isLoading } = useQuery({
    queryKey: ["segments"],
    queryFn: getSegments,
  });

  const decoded = segments.map((seg, i) => ({
    seg,
    color: segColor(i),
    positions: seg.polyline ? decode(seg.polyline) : [],
  }));

  const allPositions = decoded.flatMap((d) => d.positions);

  function handleSelect(id) {
    setSelectedId(id);
    cardRefs.current[id]?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  return (
    <div className="page">
      {/* Map */}
      <div className="map-container" style={{ height: 380, marginBottom: 24 }}>
        <MapContainer
          center={[51.505, -0.09]}
          zoom={12}
          scrollWheelZoom
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {allPositions.length > 0 && <FitAll positions={allPositions} />}
          <FlyToSegment decoded={decoded} selectedId={selectedId} />
          {decoded.map(({ seg, color, positions }) =>
            positions.length >= 2 ? (
              <Polyline
                key={seg.id}
                positions={positions}
                pathOptions={{
                  color,
                  weight: selectedId === seg.id ? 7 : 4,
                  opacity: selectedId === seg.id ? 1 : 0.75,
                }}
                eventHandlers={{ click: () => handleSelect(seg.id) }}
              />
            ) : null
          )}
        </MapContainer>
      </div>

      {/* Segment cards */}
      <h3 className="section-title">Popular Segments</h3>

      {isLoading && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton" style={{ height: 120, borderRadius: "var(--radius-lg)" }} />
          ))}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {decoded.map(({ seg, color }) => (
          <SegmentCard
            key={seg.id}
            seg={seg}
            color={color}
            selected={selectedId === seg.id}
            onSelect={handleSelect}
            cardRef={(el) => (cardRefs.current[seg.id] = el)}
          />
        ))}
      </div>
    </div>
  );
}
