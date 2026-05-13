import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { register } from "../api/auth";
import { getMe } from "../api/users";
import { useAuth } from "../context/AuthContext";
import { LogoIcon } from "../components/SportIcon";
import { HERO_IMAGES } from "../constants/images";

function apiError(err, fallback) {
  const detail = err?.response?.data?.detail;
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((e) => e.msg).join(", ");
  return fallback;
}

function passwordError(pw) {
  if (pw.length < 8) return "At least 8 characters";
  if (pw.length > 72) return "At most 72 characters";
  if (!/[A-Z]/.test(pw)) return "At least one uppercase letter";
  if (!/[a-z]/.test(pw)) return "At least one lowercase letter";
  if (!/\d/.test(pw)) return "At least one number";
  return null;
}

export default function Register() {
  const { saveToken, setUser } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "" });

  const mutation = useMutation({
    mutationFn: register,
    onSuccess: async ({ access_token, refresh_token }) => {
      saveToken(access_token, refresh_token);
      const me = await getMe();
      setUser(me);
      navigate("/feed");
    },
  });

  const pwError = form.password ? passwordError(form.password) : null;

  function handleSubmit(e) {
    e.preventDefault();
    if (passwordError(form.password)) return;
    mutation.mutate(form);
  }

  return (
    <div className="auth-page">
      <div className="auth-hero-panel" style={{ backgroundImage: `url(${HERO_IMAGES.auth})` }}>
        <div className="auth-hero-overlay">
          <div className="auth-hero-content">
            <LogoIcon size={48} />
            <h2>Your journey starts here.</h2>
            <p>Track every step, every ride, every lap. Share with friends and crush your goals.</p>
          </div>
        </div>
      </div>

      <div className="auth-form-panel">
        <div className="auth-card">
          <div className="auth-brand">
            <div className="auth-brand-logo">
              <LogoIcon size={36} />
              <h1>RunBanditsRun</h1>
            </div>
            <p>Join the community. Start tracking.</p>
          </div>

          <div className="card">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  value={form.username}
                  onChange={(e) => setForm({ ...form, username: e.target.value })}
                  placeholder="alex_runner"
                  autoComplete="username"
                  required
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  placeholder="you@example.com"
                  autoComplete="email"
                  required
                />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  placeholder="Choose a strong password"
                  autoComplete="new-password"
                  maxLength={72}
                  required
                />
                {pwError && (
                  <span style={{ fontSize: "var(--text-xs)", color: "var(--danger)" }}>{pwError}</span>
                )}
              </div>

              {mutation.isError && (
                <div className="error">{apiError(mutation.error, "Registration failed")}</div>
              )}

              <button className="btn-primary btn-full" type="submit" disabled={mutation.isPending || !!pwError}>
                {mutation.isPending ? (
                  <><div className="spinner" /> Creating account...</>
                ) : (
                  "Create Account"
                )}
              </button>
            </form>
          </div>

          <div className="auth-footer">
            Already have an account? <Link to="/login">Log in</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
