import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, setSessionExpiredHandler, tokens } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // If there's a stored token we must check it before deciding what to render.
  const [loading, setLoading] = useState(Boolean(tokens.access));

  const logout = useCallback(() => {
    tokens.clear();
    setUser(null);
  }, []);

  useEffect(() => {
    setSessionExpiredHandler(() => setUser(null));
  }, []);

  useEffect(() => {
    if (!tokens.access) return;
    api
      .me()
      .then(setUser)
      .catch(() => tokens.clear())
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await api.login({ email, password });
    tokens.set({ access: data.access_token, refresh: data.refresh_token });
    setUser(await api.me());
  }, []);

  const register = useCallback(
    async (fullName, email, password) => {
      await api.register({ full_name: fullName, email, password });
      await login(email, password);
    },
    [login]
  );

  const value = useMemo(
    () => ({ user, setUser, loading, login, register, logout, isAdmin: user?.role === "admin" }),
    [user, loading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
