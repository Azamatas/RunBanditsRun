import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { login } from "../api/auth";
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

export default function Login() {
  const { saveToken, setUser } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });

  const mutation = useMutation({
    mutationFn: login,
    onSuccess: async ({ access_token, refresh_token }) => {
      saveToken(access_token, refresh_token);
      const me = await getMe();
      setUser(me);
      navigate("/feed");
    },
  });

  function handleSubmit(e) {
    e.preventDefault();
    mutation.mutate(form);
  }

  return (
    <div className="auth-page">
      <div className="auth-hero-panel" style={{ backgroundImage: `url(${HERO_IMAGES.auth})` }}>
        <div className="auth-hero-overlay">
          <div className="auth-hero-content">
            <LogoIcon size={48} />
            <h2>Run further. Push harder. Track everything.</h2>
            <p>Join thousands of athletes logging their runs, rides, hikes, and more.</p>
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
            <p>Track your runs. Crush your goals.</p>
          </div>

          <div className="card">
            <form onSubmit={handleSubmit}>
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
                  placeholder="Your password"
                  autoComplete="current-password"
                  required
                />
              </div>

              {mutation.isError && (
                <div className="error">{apiError(mutation.error, "Login failed")}</div>
              )}

              <button className="btn-primary btn-full" type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? (
                  <><div className="spinner" /> Logging in...</>
                ) : (
                  "Log In"
                )}
              </button>
            </form>
          </div>

          <div className="auth-footer">
            Don't have an account? <Link to="/register">Sign up</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
