"use client";

import { useEffect } from "react";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthGate } from "@/components/auth/AuthGate";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { wireBackendAuth } from "@/lib/api/backend";
import { useAuthStore } from "@/store/authStore";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  // Wire the axios interceptor → store bridge exactly once on mount.
  useEffect(() => {
    wireBackendAuth({
      getToken: () => useAuthStore.getState().token,
      on401: () => useAuthStore.getState().handle401(),
    });
  }, []);

  return (
    <TooltipProvider>
      <AuthGate>
        <div className="min-h-screen bg-[color:var(--app-bg)]">
          <Sidebar />
          <div className="pl-64">
            <TopBar />
            <main>{children}</main>
          </div>
        </div>
      </AuthGate>
      <Toaster richColors closeButton position="top-right" />
    </TooltipProvider>
  );
}
