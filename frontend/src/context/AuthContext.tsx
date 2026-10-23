"use client";

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
import { authApi } from "@/lib/api";

interface AuthContextValue {
  isAuthenticated: boolean;
  username: string | null;
  isLoading: boolean;
  login: (username: string, accessToken: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Rehydrate auth state from localStorage on mount
    const authenticated = authApi.isAuthenticated();
    const storedUsername = authApi.getUsername();
    setIsAuthenticated(authenticated);
    setUsername(storedUsername);
    setIsLoading(false);
  }, []);

  const login = useCallback((username: string, accessToken: string) => {
    setIsAuthenticated(true);
    setUsername(username);
  }, []);

  const logout = useCallback(() => {
    authApi.logout();
    setIsAuthenticated(false);
    setUsername(null);
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, username, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
