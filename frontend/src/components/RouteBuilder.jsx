import { useState, useEffect } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMapEvents } from "react-leaflet";
import polylineCodec from "@mapbox/polyline";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const DEFAULT_CENTER = [51.505, -0.09];

function haversineKm([lat1, lon1], [lat2, lon2]) {
  const R = 6371;
  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLon = (lon2 - lon1) * (Math.PI / 180);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function totalKm(points) {
  let d = 0;
  for (let i = 1; i < points.length; i++) d += haversineKm(points[i - 1], points[i]);
  return d;
}

function segmentKm(points, i) {
  return haversineKm(points[i], points[i + 1]);
}

function dotIcon(color) {
  return L.divIcon({
    className: "",
    html: `<div style="width:10px;height:10px;background:${color};border-radius:50%;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.35)"></div>`,
    iconSize: [10, 10],
    iconAnchor: [5, 5],
  });
}

function segLabelIcon(label) {
  return L.divIcon({
    className: "",
    html: `<div style="background:rgba(255,255,255,0.92);border:1.5px solid var(--border,#e4e4e7);border-radius:6px;padding:2px 7px;font-size:11px;font-weight:600;color:#3f3f46;white-space:nowrap;box-shadow:0 1px 4px rgba(0,0,0,0.15);cursor:pointer">${label}</div>`,
    iconAnchor: [0, 0],
  });
}

function ClickHandler({ onAdd }) {
  useMapEvents({ click: (e) => onAdd([e.latlng.lat, e.latlng.lng]) });
  return null;
}

function fmtTime(totalMinutes) {
  const m = Math.floor(totalMinutes);
  const s = Math.round((totalMinutes - m) * 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function RouteBuilder({ onChange, onDistance, onDuration }) {
  const [points, setPoints] = useState([]);
  const [segTimes, setSegTimes] = useState([]); // minutes per segment (string for input)
  const [center, setCenter] = useState(DEFAULT_CENTER);

  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      (pos) => setCenter([pos.coords.latitude, pos.coords.longitude]),
      () => {},
    );
  }, []);

  function update(nextPoints, nextTimes) {
    setPoints(nextPoints);
    setSegTimes(nextTimes);
    onChange(nextPoints.length >= 2 ? polylineCodec.encode(nextPoints) : "");
    onDistance?.(nextPoints.length >= 2 ? totalKm(nextPoints) : 0);
    const total = nextTimes.reduce((s, t) => s + (parseFloat(t) || 0), 0);
    onDuration?.(total);
  }

  function addPoint(pt) {
    update([...points, pt], [...segTimes, ""]);
  }

  function undo() {
    update(points.slice(0, -1), segTimes.slice(0, -1));
  }

  function clear() {
    update([], []);
  }

  function setSegTime(i, val) {
    const next = [...segTimes];
    next[i] = val;
    setSegTimes(next);
    const total = next.reduce((s, t) => s + (parseFloat(t) || 0), 0);
    onDuration?.(total);
  }

  const segCount = points.length - 1;
  const totalMin = segTimes.reduce((s, t) => s + (parseFloat(t) || 0), 0);

  return (
    <div>
      <div className="map-container" style={{ height: 320, cursor: "crosshair" }}>
        <MapContainer center={center} zoom={13} scrollWheelZoom style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <ClickHandler onAdd={addPoint} />
          {points.length >= 2 && (
            <Polyline positions={points} pathOptions={{ color: "var(--accent)", weight: 4, opacity: 0.85 }} />
          )}
          {points.map((pt, i) => (
            <Marker
              key={i}
              position={pt}
              icon={dotIcon(i === 0 ? "#16a34a" : i === points.length - 1 ? "#e11d48" : "var(--accent)")}
            />
          ))}
          {Array.from({ length: segCount }, (_, i) => {
            const mid = [(points[i][0] + points[i + 1][0]) / 2, (points[i][1] + points[i + 1][1]) / 2];
            const label = segTimes[i] ? `${segTimes[i]} min` : `seg ${i + 1}`;
            return (
              <Marker key={`mid-${i}`} position={mid} icon={segLabelIcon(label)}>
                <Popup closeButton={false} autoPan={false}>
                  <div style={{ display: "flex", flexDirection: "column", gap: 4, minWidth: 130 }}>
                    <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted,#a1a1aa)" }}>
                      Segment {i + 1} · {segmentKm(points, i).toFixed(2)} km
                    </span>
                    <input
                      type="number"
                      min="0"
                      step="0.5"
                      value={segTimes[i]}
                      onChange={(e) => setSegTime(i, e.target.value)}
                      placeholder="minutes"
                      autoFocus
                      style={{ padding: "4px 8px", fontSize: 13, borderRadius: 6, border: "1.5px solid #e4e4e7", width: "100%" }}
                    />
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 8, alignItems: "center" }}>
        <button type="button" className="btn-secondary" onClick={undo} disabled={points.length === 0}>
          Undo
        </button>
        <button type="button" className="btn-secondary" onClick={clear} disabled={points.length === 0}>
          Clear
        </button>
        <span style={{ fontSize: "var(--text-xs)", color: "var(--text-muted)", marginLeft: "auto" }}>
          {points.length === 0
            ? "Click on the map to draw your route"
            : points.length === 1
            ? "1 point — add more to draw a route"
            : `${totalKm(points).toFixed(2)} km · ${points.length} points`}
        </span>
      </div>

      {segCount > 0 && (
        <div style={{ marginTop: 12, border: "1px solid var(--border)", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
          <div style={{
            display: "grid", gridTemplateColumns: "2rem 1fr 1fr 1fr",
            padding: "6px 12px",
            background: "var(--gray-50)",
            borderBottom: "1px solid var(--border)",
            fontSize: "var(--text-xs)", fontWeight: 600, color: "var(--text-muted)",
            textTransform: "uppercase", letterSpacing: "0.05em",
          }}>
            <span>#</span>
            <span>Distance</span>
            <span>Time (min)</span>
            <span>Pace</span>
          </div>
          {Array.from({ length: segCount }, (_, i) => {
            const km = segmentKm(points, i);
            const min = parseFloat(segTimes[i]) || 0;
            const pace = min > 0 && km > 0 ? fmtTime(min / km) : "—";
            return (
              <div key={i} style={{
                display: "grid", gridTemplateColumns: "2rem 1fr 1fr 1fr",
                padding: "6px 12px", alignItems: "center",
                borderBottom: i < segCount - 1 ? "1px solid var(--gray-100)" : "none",
                fontSize: "var(--text-sm)",
              }}>
                <span style={{ color: "var(--text-muted)", fontWeight: 600 }}>{i + 1}</span>
                <span>{km.toFixed(2)} km</span>
                <input
                  type="number"
                  min="0"
                  step="0.5"
                  value={segTimes[i]}
                  onChange={(e) => setSegTime(i, e.target.value)}
                  placeholder="—"
                  style={{ width: 72, padding: "4px 8px", fontSize: "var(--text-sm)" }}
                />
                <span style={{ color: "var(--text-muted)" }}>{pace} /km</span>
              </div>
            );
          })}
          {segCount > 1 && (
            <div style={{
              display: "grid", gridTemplateColumns: "2rem 1fr 1fr 1fr",
              padding: "6px 12px",
              background: "var(--gray-50)",
              borderTop: "1px solid var(--border)",
              fontSize: "var(--text-sm)", fontWeight: 700,
            }}>
              <span />
              <span>{totalKm(points).toFixed(2)} km</span>
              <span>{totalMin > 0 ? fmtTime(totalMin) : "—"}</span>
              <span style={{ color: "var(--text-muted)" }}>
                {totalMin > 0 && totalKm(points) > 0 ? `${fmtTime(totalMin / totalKm(points))} /km` : "—"}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
