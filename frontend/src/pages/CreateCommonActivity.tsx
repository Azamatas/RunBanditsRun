import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { createCommonActivity } from "../api/commonActivities";
import SportIcon from "../components/SportIcon";
import RouteBuilder from "../components/RouteBuilder";
import { SPORT_THUMBNAILS } from "../constants/images";

function apiError(err: unknown, fallback: string): string {
  const detail = (err as any)?.response?.data?.detail;
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((e: any) => e.msg).join(", ");
  return fallback;
}

const SPORTS = [
  { value: "run", label: "Run" },
  { value: "ride", label: "Ride" },
  { value: "walk", label: "Walk" },
  { value: "hike", label: "Hike" },
];

const DRAFT_KEY = "create_common_activity_draft";

export default function CreateCommonActivity() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [sportType, setSportType] = useState("run");
  const [polyline, setPolyline] = useState("");

  useEffect(() => {
    try {
      const saved = localStorage.getItem(DRAFT_KEY);
      if (saved) {
        const draft = JSON.parse(saved);
        setName(draft.name ?? "");
        setSportType(draft.sportType ?? "run");
        setPolyline(draft.polyline ?? "");
      }
    } catch {
      /* ignore corrupt draft */
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(
      DRAFT_KEY,
      JSON.stringify({ name, sportType, polyline }),
    );
  }, [name, sportType, polyline]);

  const mutation = useMutation({
    mutationFn: createCommonActivity,
    onSuccess: (ca) => {
      localStorage.removeItem(DRAFT_KEY);
      navigate(`/activities?common=${ca.id}`);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    mutation.mutate({ name, sport_type: sportType as any, polyline });
  }

  return (
    <div className="page">
      <h2 className="section-title" style={{ marginBottom: 24 }}>
        Create Common Activity
      </h2>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Sport</label>
            <div className="sport-selector">
              {SPORTS.map((s) => (
                <button
                  type="button"
                  key={s.value}
                  className={`sport-option${sportType === s.value ? " active" : ""}`}
                  onClick={() => setSportType(s.value)}
                >
                  <div
                    className="sport-option-image"
                    style={{ backgroundImage: `url(${SPORT_THUMBNAILS[s.value]})` }}
                  >
                    <div className="sport-option-image-overlay">
                      <SportIcon sport={s.value} size={22} color="currentColor" />
                    </div>
                  </div>
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Name</label>
            <input
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Central Park Loop"
            />
          </div>

          <div className="form-group">
            <label>Route</label>
            <RouteBuilder
              onChange={(encoded) => setPolyline(encoded)}
            />
          </div>

          {mutation.isError && (
            <div className="error">{apiError(mutation.error, "Failed to create common activity")}</div>
          )}

          <button
            className="btn-primary btn-full"
            type="submit"
            disabled={mutation.isPending || !polyline}
            style={{ marginTop: 8 }}
          >
            {mutation.isPending ? (
              <>
                <div className="spinner" /> Creating...
              </>
            ) : (
              "Create Common Activity"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
