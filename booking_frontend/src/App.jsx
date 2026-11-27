import { Navigate, NavLink, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "./AuthContext";
import AuthPage from "./pages/AuthPage";
import Bookings from "./pages/Bookings";
import Profile from "./pages/Profile";
import Admin from "./pages/Admin";

function Layout() {
  const { user, logout, isAdmin } = useAuth();
  return (
    <>
      <header className="topbar">
        <strong className="brand">Booking System</strong>
        <nav>
          <NavLink to="/bookings">Bookings</NavLink>
          <NavLink to="/profile">Profile</NavLink>
          {isAdmin && <NavLink to="/admin">Admin</NavLink>}
        </nav>
        <div className="spacer" />
        <span className="muted">{user.full_name}</span>
        <button className="btn ghost" onClick={logout}>
          Log out
        </button>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </>
  );
}

// Redirects to /login when signed out.
function RequireAuth() {
  const { user, loading } = useAuth();
  if (loading) return <p className="center muted">Loading…</p>;
  return user ? <Layout /> : <Navigate to="/login" replace />;
}

function RequireAdmin({ children }) {
  const { isAdmin } = useAuth();
  return isAdmin ? children : <Navigate to="/bookings" replace />;
}

// Signed-in users don't need the login/register screens.
function GuestOnly({ mode }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="center muted">Loading…</p>;
  return user ? <Navigate to="/bookings" replace /> : <AuthPage mode={mode} />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<GuestOnly mode="login" />} />
      <Route path="/register" element={<GuestOnly mode="register" />} />
      <Route element={<RequireAuth />}>
        <Route path="/bookings" element={<Bookings />} />
        <Route path="/profile" element={<Profile />} />
        <Route
          path="/admin"
          element={
            <RequireAdmin>
              <Admin />
            </RequireAdmin>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/bookings" replace />} />
    </Routes>
  );
}
