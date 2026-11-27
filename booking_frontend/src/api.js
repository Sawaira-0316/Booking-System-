// Small fetch wrapper for the FastAPI backend.
// - Adds the Bearer token to every request.
// - On a 401, tries the refresh token once, then retries the request.
// - Throws ApiError with a readable message (FastAPI "detail" can be a
//   string or a list of validation errors).

const BASE = "/api";

const ACCESS_KEY = "booking.access_token";
const REFRESH_KEY = "booking.refresh_token";

export const tokens = {
  get access() {
    return localStorage.getItem(ACCESS_KEY);
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY);
  },
  set({ access, refresh }) {
    if (access) localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

function messageFromDetail(detail, fallback) {
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        const field = Array.isArray(d.loc) ? d.loc.slice(1).join(".") : "";
        return field ? `${field}: ${d.msg}` : d.msg;
      })
      .join("; ");
  }
  return fallback;
}

// Let the AuthContext know the session is dead (refresh failed).
let onSessionExpired = () => {};
export function setSessionExpiredHandler(fn) {
  onSessionExpired = fn;
}

let refreshing = null;
async function refreshAccessToken() {
  if (!tokens.refresh) return false;
  // Share one in-flight refresh between concurrent requests.
  if (!refreshing) {
    refreshing = fetch(`${BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: tokens.refresh }),
    })
      .then(async (res) => {
        if (!res.ok) return false;
        const data = await res.json();
        tokens.set({ access: data.access_token });
        return true;
      })
      .catch(() => false)
      .finally(() => {
        refreshing = null;
      });
  }
  return refreshing;
}

async function request(path, { method = "GET", body, query, auth = true } = {}, retry = true) {
  const url = new URL(`${BASE}${path}`, window.location.origin);
  if (query) {
    Object.entries(query).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, v);
    });
  }

  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (auth && tokens.access) headers.Authorization = `Bearer ${tokens.access}`;

  let res;
  try {
    res = await fetch(url, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError("Cannot reach the server. Is the backend running on port 8000?", 0);
  }

  if (res.status === 401 && auth && retry && tokens.refresh) {
    if (await refreshAccessToken()) {
      return request(path, { method, body, query, auth }, false);
    }
    tokens.clear();
    onSessionExpired();
  }

  const data = res.status === 204 ? null : await res.json().catch(() => null);

  if (!res.ok) {
    throw new ApiError(messageFromDetail(data?.detail, `Request failed (${res.status})`), res.status);
  }
  return data;
}

export const api = {
  // auth
  register: (body) => request("/auth/register", { method: "POST", body, auth: false }),
  login: (body) => request("/auth/login", { method: "POST", body, auth: false }),

  // users
  me: () => request("/users/me"),
  updateMe: (body) => request("/users/me", { method: "PUT", body }),

  // bookings (note the trailing slash on the collection routes: FastAPI redirects without it)
  listBookings: (query) => request("/bookings/", { query }),
  createBooking: (body) => request("/bookings/", { method: "POST", body }),
  updateBooking: (id, body) => request(`/bookings/${id}`, { method: "PUT", body }),
  deleteBooking: (id) => request(`/bookings/${id}`, { method: "DELETE" }),

  // admin
  adminUsers: () => request("/admin/users"),
  setUserRole: (id, role) => request(`/admin/users/${id}/role`, { method: "PATCH", body: { role } }),
};
