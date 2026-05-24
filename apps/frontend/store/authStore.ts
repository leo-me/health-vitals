"use client";

import { create } from "zustand";
import { toast } from "sonner";
import { decodeToken, isExpired } from "@/lib/jwt";

const TOKEN_STORAGE_KEY = "hv.token";

type LogoutReason = "user" | "401" | "expired";

interface AuthState {
  token: string | null;
  userId: string | null;
  expiresAt: number | null; // ms epoch
  hydrated: boolean;
  status: "idle" | "authenticating";

  hydrate: () => void;
  login: (token: string) => void;
  logout: (reason?: LogoutReason) => void;
  handle401: () => void;
  setStatus: (status: AuthState["status"]) => void;
}

// Module-scoped timer id so the store stays plain-data and serializable.
let expiryTimer: ReturnType<typeof setTimeout> | null = null;

function clearExpiryTimer() {
  if (expiryTimer) {
    clearTimeout(expiryTimer);
    expiryTimer = null;
  }
}

function scheduleExpiry(expiresAt: number, onExpire: () => void) {
  clearExpiryTimer();
  const ms = Math.max(0, expiresAt - Date.now());
  expiryTimer = setTimeout(onExpire, ms);
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: null,
  userId: null,
  expiresAt: null,
  hydrated: false,
  status: "idle",

  hydrate: () => {
    if (get().hydrated) return;
    if (typeof window === "undefined") {
      set({ hydrated: true });
      return;
    }
    try {
      const stored = window.localStorage.getItem(TOKEN_STORAGE_KEY);
      if (stored) {
        const claims = decodeToken(stored);
        if (claims.exp && !isExpired(claims.exp)) {
          const expiresAt = claims.exp * 1000;
          scheduleExpiry(expiresAt, () => get().logout("expired"));
          set({
            token: stored,
            userId: claims.sub,
            expiresAt,
            hydrated: true,
          });
          return;
        }
        // Token was present but invalid/expired — clean it up.
        window.localStorage.removeItem(TOKEN_STORAGE_KEY);
      }
    } catch {
      // Corrupted token in storage — clear it silently.
      try {
        window.localStorage.removeItem(TOKEN_STORAGE_KEY);
      } catch {
        /* noop */
      }
    }
    set({ hydrated: true });
  },

  login: (token) => {
    const claims = decodeToken(token);
    const expiresAt = claims.exp * 1000;
    try {
      window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
    } catch {
      /* localStorage may throw in private mode — non-fatal */
    }
    scheduleExpiry(expiresAt, () => get().logout("expired"));
    set({
      token,
      userId: claims.sub,
      expiresAt,
      status: "idle",
    });
  },

  logout: (reason: LogoutReason = "user") => {
    clearExpiryTimer();
    try {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    } catch {
      /* noop */
    }
    set({ token: null, userId: null, expiresAt: null, status: "idle" });
    if (reason === "401") {
      toast.error("Session expired. Please sign in again.");
    } else if (reason === "expired") {
      toast.message("Your session has expired.");
    }
  },

  handle401: () => {
    if (get().token) {
      get().logout("401");
    }
  },

  setStatus: (status) => set({ status }),
}));
