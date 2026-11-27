import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../AuthContext";
import { formatDate } from "../dates";

export default function Admin() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .adminUsers()
      .then(setUsers)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function changeRole(id, role) {
    setError("");
    try {
      const updated = await api.setUserRole(id, role);
      setUsers((list) => list.map((u) => (u.id === id ? updated : u)));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h1>Users</h1>
      {error && <p className="error">{error}</p>}
      {loading ? (
        <p className="muted">Loading…</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Active</th>
                <th>Joined</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.id}</td>
                  <td>{u.full_name}</td>
                  <td>{u.email}</td>
                  <td>{u.is_active ? "Yes" : "No"}</td>
                  <td>{formatDate(u.created_at)}</td>
                  <td>
                    <select
                      value={u.role}
                      onChange={(e) => changeRole(u.id, e.target.value)}
                      disabled={u.id === me.id} // don't let an admin demote themselves by accident
                      title={u.id === me.id ? "You can't change your own role" : ""}
                    >
                      <option value="user">user</option>
                      <option value="admin">admin</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
