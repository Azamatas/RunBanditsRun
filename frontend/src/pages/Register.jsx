import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { register } from "../api/auth";
import { getMe } from "../api/users";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { saveToken, setUser } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "" });

  const mutation = useMutation({
    mutationFn: register,
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
                required
              />
            </div>

            {mutation.isError && (
              <div className="error">{mutation.error?.response?.data?.detail ?? "Registration failed"}</div>
            )}

            <button className="btn-primary btn-full" type="submit" disabled={mutation.isPending}>
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
  );
}
