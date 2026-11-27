import { useState } from "react";
import { api } from "../api";
import { parseApiDate } from "../dates";

// <input type="datetime-local"> wants "YYYY-MM-DDTHH:mm" in LOCAL time,
// the API speaks ISO 8601. These two helpers convert between them.
function toLocalInput(iso) {
  if (!iso) return "";
  const d = parseApiDate(iso);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}
const toIso = (local) => new Date(local).toISOString();

export default function BookingForm({ booking, statuses, onClose, onSaved }) {
  const editing = Boolean(booking);

  const [form, setForm] = useState({
    title: booking?.title ?? "",
    notes: booking?.notes ?? "",
    booking_date: toLocalInput(booking?.booking_date),
    status: booking?.status ?? "pending",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const payload = {
        title: form.title.trim(),
        notes: form.notes.trim() || null,
        booking_date: toIso(form.booking_date),
      };
      if (editing) await api.updateBooking(booking.id, { ...payload, status: form.status });
      else await api.createBooking(payload);
      onSaved();
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <form className="card modal" onSubmit={onSubmit}>
        <h2>{editing ? "Edit booking" : "New booking"}</h2>

        <label>
          Title
          <input value={form.title} onChange={set("title")} minLength={2} maxLength={255} required autoFocus />
        </label>

        <label>
          Date & time
          <input type="datetime-local" value={form.booking_date} onChange={set("booking_date")} required />
        </label>

        {editing && (
          <label>
            Status
            <select value={form.status} onChange={set("status")}>
              {statuses.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </label>
        )}

        <label>
          Notes
          <textarea rows={3} value={form.notes} onChange={set("notes")} />
        </label>

        {error && <p className="error">{error}</p>}

        <div className="row end">
          <button type="button" className="btn ghost" onClick={onClose}>
            Cancel
          </button>
          <button className="btn primary" disabled={busy}>
            {busy ? "Saving…" : editing ? "Save changes" : "Create booking"}
          </button>
        </div>
      </form>
    </div>
  );
}
