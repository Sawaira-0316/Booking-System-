import { useState } from "react";
import { api } from "../api";
import { useAuth } from "../AuthContext";
import { formatDate } from "../dates";

export default function Profile() {
  const { user, setUser } = useAuth();
  const [form, setForm] = useState({ full_name: user.full_name, email: user.email });
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setSaved(false);
    setBusy(true);
    try {
      setUser(await api.updateMe(form));
      setSaved(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="card narrow" onSubmit={onSubmit}>
      <h1>Your profile</h1>
      <label>
        Full name
        <input
          value={form.full_name}
          onChange={(e) => setForm({ ...form, full_name: e.target.value })}
          required
        />
      </label>
      <label>
        Email
        <input
          type="email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          required
        />
      </label>
      <p className="muted">
        Role: <strong>{user.role}</strong> · Member since {formatDate(user.created_at)}
      </p>
      {error && <p className="error">{error}</p>}
      {saved && <p className="success">Profile updated.</p>}
      <button className="btn primary" disabled={busy}>
        {busy ? "Saving…" : "Save changes"}
      </button>
    </form>
  );
}
