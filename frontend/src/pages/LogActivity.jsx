import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { createActivity } from "../api/activities";
import { getFollowing } from "../api/users";

const SPORTS = [
  { value: "run", icon: "\u{1F3C3}", label: "Run" },
  { value: "ride", icon: "\u{1F6B4}", label: "Ride" },
  { value: "swim", icon: "\u{1F3CA}", label: "Swim" },
  { value: "walk", icon: "\u{1F6B6}", label: "Walk" },
  { value: "hike", icon: "\u{1F97E}", label: "Hike" },
];

const VISIBILITIES = ["public", "friends", "private"];

export default function LogActivity() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: "",
    sport_type: "run",
    distance: "",
    duration: "",
    elevation: "",
    visibility: "public",
    polyline: "",
  });
  const [taggedIds, setTaggedIds] = useState([]);
  const [tagSearch, setTagSearch] = useState("");

  const { data: following } = useQuery({
    queryKey: ["following"],
    queryFn: getFollowing,
  });

  const mutation = useMutation({
    mutationFn: createActivity,
    onSuccess: (activity) => navigate(`/activities/${activity.id}`),
  });

  function set(field) {
    return (e) => setForm({ ...form, [field]: e.target.value });
  }

  function addTag(userId) {
    if (!taggedIds.includes(userId)) setTaggedIds([...taggedIds, userId]);
    setTagSearch("");
  }

  function removeTag(userId) {
    setTaggedIds(taggedIds.filter((id) => id !== userId));
  }

  const availableFriends = (following ?? []).filter(
    (f) => !taggedIds.includes(f.id) && f.username.toLowerCase().includes(tagSearch.toLowerCase()),
  );

  function handleSubmit(e) {
    e.preventDefault();
    mutation.mutate({
      ...form,
      distance: form.distance ? parseFloat(form.distance) * 1000 : null,
      duration: form.duration ? parseInt(form.duration) * 60 : null,
      elevation: form.elevation ? parseFloat(form.elevation) : null,
      polyline: form.polyline || null,
      tagged_athlete_ids: taggedIds,
    });
  }

  return (
    <div className="page">
      <h2 className="section-title" style={{ marginBottom: 24 }}>Log Activity</h2>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Sport</label>
            <div className="sport-selector">
              {SPORTS.map((s) => (
                <button
                  type="button"
                  key={s.value}
                  className={`sport-option${form.sport_type === s.value ? " active" : ""}`}
                  onClick={() => setForm({ ...form, sport_type: s.value })}
                >
                  <span className="sport-icon">{s.icon}</span>
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Title</label>
            <input required value={form.title} onChange={set("title")} placeholder="Morning Run" />
          </div>

          <div className="form-row form-row-3">
            <div className="form-group">
              <label>Distance (km)</label>
              <input type="number" step="0.01" min="0" value={form.distance} onChange={set("distance")} placeholder="5.0" />
            </div>
            <div className="form-group">
              <label>Duration (min)</label>
              <input type="number" min="0" value={form.duration} onChange={set("duration")} placeholder="30" />
            </div>
            <div className="form-group">
              <label>Elevation (m)</label>
              <input type="number" min="0" value={form.elevation} onChange={set("elevation")} placeholder="120" />
            </div>
          </div>

          <div className="form-group">
            <label>Visibility</label>
            <div className="pill-group">
              {VISIBILITIES.map((v) => (
                <button
                  type="button"
                  key={v}
                  className={`pill-option${form.visibility === v ? " active" : ""}`}
                  onClick={() => setForm({ ...form, visibility: v })}
                >
                  {v}
                </button>
              ))}
            </div>
          </div>

          {/* Tag athletes */}
          <div className="form-group">
            <label>Tag Athletes <span style={{ fontWeight: 400, color: "var(--text-muted)" }}>(optional)</span></label>
            <input
              value={tagSearch}
              onChange={(e) => setTagSearch(e.target.value)}
              placeholder="Search friends to tag..."
            />
            {tagSearch && availableFriends.length > 0 && (
              <div style={{ border: "1px solid var(--border)", borderRadius: "var(--radius-md)", marginTop: 4, maxHeight: 150, overflowY: "auto" }}>
                {availableFriends.map((f) => (
                  <button
                    type="button"
                    key={f.id}
                    onClick={() => addTag(f.id)}
                    style={{
                      display: "block", width: "100%", textAlign: "left",
                      padding: "8px 12px", background: "none", border: "none",
                      fontSize: "var(--text-sm)", cursor: "pointer", fontFamily: "var(--font)",
                    }}
                    onMouseEnter={(e) => (e.target.style.background = "var(--gray-50)")}
                    onMouseLeave={(e) => (e.target.style.background = "none")}
                  >
                    {f.username}
                  </button>
                ))}
              </div>
            )}
            {taggedIds.length > 0 && (
              <div className="tag-chips">
                {taggedIds.map((id) => {
                  const f = (following ?? []).find((u) => u.id === id);
                  return (
                    <span className="tag-chip" key={id}>
                      {f?.username ?? `#${id}`}
                      <button type="button" className="tag-chip-remove" onClick={() => removeTag(id)}>&times;</button>
                    </span>
                  );
                })}
              </div>
            )}
          </div>

          <div className="form-group">
            <label>Route Polyline <span style={{ fontWeight: 400, color: "var(--text-muted)" }}>(optional)</span></label>
            <input value={form.polyline} onChange={set("polyline")} placeholder="Paste encoded route string" />
          </div>

          {mutation.isError && (
            <div className="error">{mutation.error?.response?.data?.detail ?? "Failed to save activity"}</div>
          )}

          <button className="btn-primary btn-full" type="submit" disabled={mutation.isPending} style={{ marginTop: 8 }}>
            {mutation.isPending ? (<><div className="spinner" /> Saving...</>) : "Save Activity"}
          </button>
        </form>
      </div>
    </div>
  );
}
