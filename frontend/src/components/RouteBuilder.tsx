import { useState, useEffect } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMapEvents } from "react-leaflet";
import polylineCodec from "@mapbox/polyline";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export const ROUTE_DRAFT_KEY = "route_builder_draft";

const DEFAULT_CENTER = [51.505, -0.09];

type LatLng = [number, number];

interface RouteBuilderProps {
  onChange: (encodedPolyline: string) => void;
  onDistance?: (km: number) => void;
  onDuration?: (totalMinutes: number) => void;
}

function haversineKm([lat1, lon1]: LatLng, [lat2, lon2]: LatLng): number {
  const R = 6371;
  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLon = (lon2 - lon1) * (Math.PI / 180);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function totalKm(points: LatLng[]): number {
  let d = 0;
  for (let i = 1; i < points.length; i++) d += haversineKm(points[i - 1], points[i]);
  return d;
}

function legKm(points: LatLng[], i: number): number {
  return haversineKm(points[i], points[i + 1]);
}

function dotIcon(color: string) {
  return L.divIcon({
    className: "",
    html: `<div style="width:10px;height:10px;background:${color};border-radius:50%;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.35)"></div>`,
    iconSize: [10, 10],
    iconAnchor: [5, 5],
  });
}

function legLabelIcon(label: string) {
  return L.divIcon({
    className: "",
    html: `<div style="background:rgba(255,255,255,0.92);border:1.5px solid var(--border,#e4e4e7);border-radius:6px;padding:2px 7px;font-size:11px;font-weight:600;color:#3f3f46;white-space:nowrap;box-shadow:0 1px 4px rgba(0,0,0,0.15);cursor:pointer">${label}</div>`,
    iconAnchor: [0, 0],
  });
}

function ClickHandler({ onAdd }: { onAdd: (pt: LatLng) => void }) {
  useMapEvents({ click: (e) => onAdd([e.latlng.lat, e.latlng.lng]) });
  return null;
}

function fmtTime(totalMinutes: number): string {
  const m = Math.floor(totalMinutes);
  const s = Math.round((totalMinutes - m) * 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function RouteBuilder({ onChange, onDistance, onDuration }: RouteBuilderProps) {
  const [points, setPoints] = useState<LatLng[]>([]);
  const [legTimes, setLegTimes] = useState<string[]>([]); // minutes per leg (string for input)
  const [center, setCenter] = useState<LatLng>(DEFAULT_CENTER as LatLng);

  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      (pos) => setCenter([pos.coords.latitude, pos.coords.longitude]),
      () => {},
    );
  }, []);

  function update(nextPoints: LatLng[], nextTimes: string[]) {
    setPoints(nextPoints);
    setLegTimes(nextTimes);
    onChange(nextPoints.length >= 2 ? polylineCodec.encode(nextPoints) : "");
    onDistance?.(nextPoints.length >= 2 ? totalKm(nextPoints) : 0);
    const total = nextTimes.reduce((s, t) => s + (parseFloat(t) || 0), 0);
    onDuration?.(total);
  }

  function addPoint(pt: LatLng) {
    update([...points, pt], [...legTimes, ""]);
  }

  function undo() {
    update(points.slice(0, -1), legTimes.slice(0, -1));
  }

  function clear() {
    update([], []);
  }

  function setLegTime(i: number, val: string) {
    const next = [...legTimes];
    next[i] = val;
    setLegTimes(next);
    const total = next.reduce((s, t) => s + (parseFloat(t) || 0), 0);
    onDuration?.(total);
  }

  const legCount = points.length - 1;
  const totalMin = legTimes.reduce((s, t) => s + (parseFloat(t) || 0), 0);

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
          {Array.from({ length: legCount }, (_, i) => {
            const mid: LatLng = [(points[i][0] + points[i + 1][0]) / 2, (points[i][1] + points[i + 1][1]) / 2];
            const label = legTimes[i] ? `${legTimes[i]} min` : `leg ${i + 1}`;
            return (
              <Marker key={`mid-${i}`} position={mid} icon={legLabelIcon(label)}>
                <Popup closeButton={false} autoPan={false}>
                  <div style={{ display: "flex", flexDirection: "column", gap: 4, minWidth: 130 }}>
                    <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted,#a1a1aa)" }}>
                      Leg {i + 1} · {legKm(points, i).toFixed(2)} km
                    </span>
                    <input
                      type="number"
                      min="0"
                      step="0.5"
                      value={legTimes[i]}
                      onChange={(e) => setLegTime(i, e.target.value)}
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

      {legCount > 0 && (
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
          {Array.from({ length: legCount }, (_, i) => {
            const km = legKm(points, i);
            const min = parseFloat(legTimes[i]) || 0;
            const pace = min > 0 && km > 0 ? fmtTime(min / km) : "—";
            return (
              <div key={i} style={{
                display: "grid", gridTemplateColumns: "2rem 1fr 1fr 1fr",
                padding: "6px 12px", alignItems: "center",
                borderBottom: i < legCount - 1 ? "1px solid var(--gray-100)" : "none",
                fontSize: "var(--text-sm)",
              }}>
                <span style={{ color: "var(--text-muted)", fontWeight: 600 }}>{i + 1}</span>
                <span>{km.toFixed(2)} km</span>
                <input
                  type="number"
                  min="0"
                  step="0.5"
                  value={legTimes[i]}
                  onChange={(e) => setLegTime(i, e.target.value)}
                  placeholder="—"
                  style={{ width: 72, padding: "4px 8px", fontSize: "var(--text-sm)" }}
                />
                <span style={{ color: "var(--text-muted)" }}>{pace} /km</span>
              </div>
            );
          })}
          {legCount > 1 && (
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
