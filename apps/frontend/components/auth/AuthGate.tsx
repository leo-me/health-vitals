"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/store/authStore";
import { LoginModal } from "./LoginModal";
import { PageSkeleton } from "@/components/common/PageSkeleton";

/**
 * Wraps the admin tree. Renders the page skeleton while auth state is
 * unresolved; overlays the LoginModal when no valid token; passes through
 * when authenticated.
 *
 * Hydration safety: the zustand store starts with `hydrated: false` on both
 * server and client. We render <PageSkeleton /> until `hydrate()` flips the
 * flag inside useEffect — so the server's first render and the client's
 * first render emit identical markup. No `Date.now()` in render because the
 * store's setTimeout invalidates the token automatically at `exp`.
 */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  console.log('token: ', token);
  const hydrated = useAuthStore((s) => s.hydrated);
  const hydrate = useAuthStore((s) => s.hydrate);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

      console.log('hydrated: ', hydrated);
      console.log('hydrated:', hydrated, '| token:', token);



  if (!hydrated) {
    return <PageSkeleton />;
  }

  if (!token) {
    return (
      <>
        <PageSkeleton />
        <LoginModal />
      </>
    );
  }

  return <>{children}</>;
}
