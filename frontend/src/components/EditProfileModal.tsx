import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateMe } from "../api/users";
import { useAuth } from "../context/AuthContext";

function apiError(err, fallback) {
  const detail = err?.response?.data?.detail;
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((e) => e.msg).join(", ");
  return fallback;
}

export default function EditProfileModal({ onClose }) {
  const { user, setUser } = useAuth();
  const qc = useQueryClient();
  const [form, setForm] = useState({
    bio: user?.bio ?? "",
    location: user?.location ?? "",
  });

  const mutation = useMutation({
    mutationFn: updateMe,
    onSuccess: (updated) => {
      setUser(updated);
      qc.invalidateQueries({ queryKey: ["stats"] });
      onClose();
    },
  });

  function handleSubmit(e) {
    e.preventDefault();
    mutation.mutate(form);
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Edit Profile</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Location</label>
              <input
                value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
                placeholder="Portland, OR"
                maxLength={100}
              />
            </div>
            <div className="form-group">
              <label>Bio</label>
              <textarea
                rows={3}
                value={form.bio}
                onChange={(e) => setForm({ ...form, bio: e.target.value })}
                placeholder="Tell us about yourself..."
                maxLength={500}
              />
            </div>

            {mutation.isError && (
              <div className="error">{apiError(mutation.error, "Failed to update profile")}</div>
            )}

            <div style={{ display: "flex", gap: 12, justifyContent: "flex-end" }}>
              <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
              <button type="submit" className="btn-primary" disabled={mutation.isPending}>
                {mutation.isPending ? "Saving..." : "Save Changes"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
