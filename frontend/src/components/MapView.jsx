import { useEffect, useMemo } from "react";
import { MapContainer, TileLayer, Polyline, useMap } from "react-leaflet";
import polylineCodec from "@mapbox/polyline";
import "leaflet/dist/leaflet.css";

function FitBounds({ positions }) {
  const map = useMap();
  useEffect(() => {
    if (positions.length > 1) {
      map.fitBounds(positions, { padding: [30, 30] });
    }
  }, [map, positions]);
  return null;
}

export default function MapView({ polyline, height = 240, sportColor = "var(--accent)" }) {
  const positions = useMemo(() => {
    if (!polyline) return [];
    try {
      return polylineCodec.decode(polyline);
    } catch {
      return [];
    }
  }, [polyline]);

  if (positions.length < 2) return null;

  const center = positions[Math.floor(positions.length / 2)];

  return (
    <div className="map-container" style={{ height }}>
      <MapContainer center={center} zoom={14} scrollWheelZoom={false} dragging={false} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Polyline positions={positions} pathOptions={{ color: sportColor, weight: 4, opacity: 0.85 }} />
        <FitBounds positions={positions} />
      </MapContainer>
    </div>
  );
}
