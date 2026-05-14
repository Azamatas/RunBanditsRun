import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getActivity, updateActivity } from "../api/activities";
import type { Activity, ActivityUpdatePayload, Visibility } from "../types/api";

function apiError(err: any, fallback: string): string {
  const detail = err?.response?.data?.detail;
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((e: any) => e.msg).join(", ");
  return fallback;
}

const VISIBILITIES: Visibility[] = ["public", "friends", "private"];

export default function EditActivity() {
  const { id } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data: activity, isLoading } = useQuery<Activity>({
    queryKey: ["activity", id],
    queryFn: () => getActivity(id!),
  });

  const [form, setForm] = useState<{ title: string; visibility: Visibility }>({ title: "", visibility: "public" });

  useEffect(() => {
    if (activity) {
      setForm({ title: activity.title, visibility: activity.visibility });
    }
  }, [activity]);

  const mutation = useMutation({
    mutationFn: (data: ActivityUpdatePayload) => updateActivity(id!, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["activity", id] });
      qc.invalidateQueries({ queryKey: ["feed"] });
      navigate(`/activities/${id}`);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.title.trim()) return;
    mutation.mutate(form);
  }

  if (isLoading) {
    return (
      <div className="page">
        <div className="skeleton" style={{ height: 200, borderRadius: "var(--radius-lg)" }} />
      </div>
    );
  }

  return (
    <div className="page">
      <h2 className="section-title" style={{ marginBottom: 24 }}>Edit Activity</h2>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Title</label>
            <input
              required
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
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

          {mutation.isError && (
            <div className="error">{apiError(mutation.error, "Failed to update activity")}</div>
          )}

          <div style={{ display: "flex", gap: 12 }}>
            <button type="button" className="btn-ghost" onClick={() => navigate(-1)}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
