"use client";
import { createContext, useContext, useEffect, useState } from "react";
import { AuthUser } from "../interfaces/main";

interface AuthContextValue {
  user: AuthUser | null;
  login: (user: AuthUser) => void;
  logout: () => void;
  isLogged: () => boolean;
  updateUserData: <K extends keyof AuthUser>(name: K, value: AuthUser[K]) => void;
}

const STORAGE_KEY = "auth_user";

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored) setUser(JSON.parse(stored));
  }, []);

  const login = (u: AuthUser) => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(u));
    setUser(u);
  };

  const logout = () => {
    window.localStorage.removeItem(STORAGE_KEY);
    setUser(null);
  };

  const updateUserData = <K extends keyof AuthUser>(name: K, value: AuthUser[K]) => {
    setUser((prev) => {
      let currentUser = prev;
      if (!currentUser) {
        const stored = window.localStorage.getItem(STORAGE_KEY);
        if (stored) {
          try {
            currentUser = JSON.parse(stored);
          } catch {
            currentUser = null;
          }
        }
      }
      if (!currentUser) return null;
      const updated = { ...currentUser, [name]: value };
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  const isLogged = () => user !== null;

  return (
    <AuthContext.Provider value={{ user, login, logout, isLogged, updateUserData }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
