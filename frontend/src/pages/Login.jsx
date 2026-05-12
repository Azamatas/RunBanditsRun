import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { login } from "../api/auth";
import { getMe } from "../api/users";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { saveToken, setUser } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });

  const mutation = useMutation({
    mutationFn: login,
    onSuccess: async ({ access_token }) => {
      saveToken(access_token);
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
      <div className="auth-card">
        <div className="auth-brand">
          <h1>RunBanditsRun</h1>
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
              />
            </div>

            {mutation.isError && (
              <div className="error">{mutation.error?.response?.data?.detail ?? "Login failed"}</div>
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
  );
}
