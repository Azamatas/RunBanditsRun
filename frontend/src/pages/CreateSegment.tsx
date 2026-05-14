import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createSegment } from "../api/segments";

export default function CreateSegment() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [form, setForm] = useState({
    name: "",
    distance: "",
    polyline: "",
  });

  const mutation = useMutation({
    mutationFn: createSegment,
    onSuccess: (segment) => {
      qc.invalidateQueries({ queryKey: ["segments"] });
      navigate(`/segments/${segment.id}`);
    },
  });

  function set(field) {
    return (e) => setForm({ ...form, [field]: e.target.value });
  }

  function handleSubmit(e) {
    e.preventDefault();
    mutation.mutate({
      name: form.name,
      distance: form.distance ? parseFloat(form.distance) * 1000 : null,
      polyline: form.polyline || null,
    });
  }

  return (
    <div className="page">
      <h2 className="section-title" style={{ marginBottom: 24 }}>Create Segment</h2>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name</label>
            <input required value={form.name} onChange={set("name")} placeholder="Morning Hill Sprint" />
          </div>

          <div className="form-group">
            <label>Distance (km)</label>
            <input type="number" step="0.01" min="0" value={form.distance} onChange={set("distance")} placeholder="5.0" />
          </div>

          <div className="form-group">
            <label>Route Polyline <span style={{ fontWeight: 400, color: "var(--text-muted)" }}>(optional)</span></label>
            <input value={form.polyline} onChange={set("polyline")} placeholder="Paste encoded route string" />
          </div>

          {mutation.isError && (
            <div className="error">{(mutation.error as any)?.response?.data?.detail ?? "Failed to create segment"}</div>
          )}

          <button className="btn-primary btn-full" type="submit" disabled={mutation.isPending} style={{ marginTop: 8 }}>
            {mutation.isPending ? (<><div className="spinner" /> Creating...</>) : "Create Segment"}
          </button>
        </form>
      </div>
    </div>
  );
}