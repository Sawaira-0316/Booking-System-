import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../AuthContext";
import BookingForm from "../components/BookingForm";
import { formatDateTime } from "../dates";

const PAGE_SIZE = 10;
const STATUSES = ["pending", "confirmed", "cancelled"];

const emptyFilters = {
  search: "",
  status: "",
  from_date: "",
  to_date: "",
  sort_by: "created_at",
  order: "desc",
};

export default function Bookings() {
  const { isAdmin } = useAuth();

  const [filters, setFilters] = useState(emptyFilters);
  // `applied` only changes when the user submits the filter form,
  // so typing in the search box doesn't fire a request per keystroke.
  const [applied, setApplied] = useState(emptyFilters);
  const [skip, setSkip] = useState(0);

  const [page, setPage] = useState({ items: [], total: 0, has_more: false });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // null = closed, {} = new booking, {…booking} = editing
  const [editing, setEditing] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setPage(await api.listBookings({ ...applied, skip, limit: PAGE_SIZE }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [applied, skip]);

  useEffect(() => {
    load();
  }, [load]);

  function applyFilters(e) {
    e.preventDefault();
    setSkip(0);
    setApplied(filters);
  }

  function resetFilters() {
    setFilters(emptyFilters);
    setApplied(emptyFilters);
    setSkip(0);
  }

  async function remove(b) {
    if (!window.confirm(`Delete "${b.title}"? This can't be undone.`)) return;
    try {
      await api.deleteBooking(b.id);
      // If that was the last item on a later page, step back one page.
      if (page.items.length === 1 && skip > 0) setSkip(Math.max(0, skip - PAGE_SIZE));
      else load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function quickStatus(b, status) {
    try {
      await api.updateBooking(b.id, { status });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  const setFilter = (field) => (e) => setFilters({ ...filters, [field]: e.target.value });
  const from = page.total === 0 ? 0 : skip + 1;
  const to = skip + page.items.length;

  return (
    <>
      <div className="row between">
        <h1>{isAdmin ? "All bookings" : "My bookings"}</h1>
        <button className="btn primary" onClick={() => setEditing({})}>
          + New booking
        </button>
      </div>

      <form className="card filters" onSubmit={applyFilters}>
        <label>
          Search title
          <input value={filters.search} onChange={setFilter("search")} maxLength={100} placeholder="e.g. dentist" />
        </label>
        <label>
          Status
          <select value={filters.status} onChange={setFilter("status")}>
            <option value="">Any</option>
            {STATUSES.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </label>
        <label>
          From
          <input type="date" value={filters.from_date} onChange={setFilter("from_date")} />
        </label>
        <label>
          To
          <input type="date" value={filters.to_date} onChange={setFilter("to_date")} />
        </label>
        <label>
          Sort by
          <select value={filters.sort_by} onChange={setFilter("sort_by")}>
            <option value="created_at">Created</option>
            <option value="booking_date">Booking date</option>
            <option value="status">Status</option>
          </select>
        </label>
        <label>
          Order
          <select value={filters.order} onChange={setFilter("order")}>
            <option value="desc">Newest first</option>
            <option value="asc">Oldest first</option>
          </select>
        </label>
        <div className="row">
          <button className="btn primary">Apply</button>
          <button type="button" className="btn ghost" onClick={resetFilters}>
            Reset
          </button>
        </div>
      </form>

      {error && <p className="error">{error}</p>}

      <div className="card">
        {loading ? (
          <p className="muted">Loading…</p>
        ) : page.items.length === 0 ? (
          <p className="muted center">No bookings found.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Notes</th>
                  {isAdmin && <th>User</th>}
                  <th />
                </tr>
              </thead>
              <tbody>
                {page.items.map((b) => (
                  <tr key={b.id}>
                    <td>
                      <strong>{b.title}</strong>
                    </td>
                    <td>{formatDateTime(b.booking_date)}</td>
                    <td>
                      <span className={`badge ${b.status}`}>{b.status}</span>
                    </td>
                    <td className="notes">{b.notes || <span className="muted">—</span>}</td>
                    {isAdmin && <td>#{b.user_id}</td>}
                    <td className="actions">
                      {b.status === "pending" && (
                        <button className="btn small" onClick={() => quickStatus(b, "confirmed")}>
                          Confirm
                        </button>
                      )}
                      {b.status !== "cancelled" && (
                        <button className="btn small" onClick={() => quickStatus(b, "cancelled")}>
                          Cancel
                        </button>
                      )}
                      <button className="btn small" onClick={() => setEditing(b)}>
                        Edit
                      </button>
                      <button className="btn small danger" onClick={() => remove(b)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="row between pager">
          <span className="muted">
            {from}–{to} of {page.total}
          </span>
          <div className="row">
            <button
              className="btn small"
              disabled={skip === 0 || loading}
              onClick={() => setSkip(Math.max(0, skip - PAGE_SIZE))}
            >
              ← Prev
            </button>
            <button className="btn small" disabled={!page.has_more || loading} onClick={() => setSkip(skip + PAGE_SIZE)}>
              Next →
            </button>
          </div>
        </div>
      </div>

      {editing && (
        <BookingForm
          booking={editing.id ? editing : null}
          statuses={STATUSES}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
            load();
          }}
        />
      )}
    </>
  );
}
