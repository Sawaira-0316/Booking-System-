import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

// One component for both /login and /register.
export default function AuthPage({ mode }) {
  const isRegister = mode === "register";
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ fullName: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (isRegister) await register(form.fullName.trim(), form.email.trim(), form.password);
      else await login(form.email.trim(), form.password);
      navigate("/bookings", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-wrap">
      <form className="card auth-card" onSubmit={onSubmit}>
        <h1>{isRegister ? "Create account" : "Sign in"}</h1>

        {isRegister && (
          <label>
            Full name
            <input
              value={form.fullName}
              onChange={set("fullName")}
              minLength={2}
              maxLength={150}
              required
              autoComplete="name"
            />
          </label>
        )}

        <label>
          Email
          <input type="email" value={form.email} onChange={set("email")} required autoComplete="email" />
        </label>

        <label>
          Password
          <input
            type="password"
            value={form.password}
            onChange={set("password")}
            minLength={isRegister ? 8 : undefined}
            maxLength={128}
            required
            autoComplete={isRegister ? "new-password" : "current-password"}
          />
          {isRegister && <small className="muted">At least 8 characters.</small>}
        </label>

        {error && <p className="error">{error}</p>}

        <button className="btn primary" disabled={busy}>
          {busy ? "Please wait…" : isRegister ? "Create account" : "Sign in"}
        </button>

        <p className="muted center">
          {isRegister ? (
            <>
              Already have an account? <Link to="/login">Sign in</Link>
            </>
          ) : (
            <>
              No account yet? <Link to="/register">Register</Link>
            </>
          )}
        </p>
      </form>
    </div>
  );
}
