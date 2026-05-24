"use client";

import { LogOut, User as UserIcon } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { CdlHealthBadge } from "./CdlHealthBadge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

export function TopBar() {
  const userId = useAuthStore((s) => s.userId);
  const logout = useAuthStore((s) => s.logout);

  const shortId = userId ? `${userId.slice(0, 8)}…${userId.slice(-4)}` : "—";

  return (
    <header className="sticky top-0 z-30 bg-background/80 backdrop-blur border-b h-14 flex items-center justify-between px-6">
      <CdlHealthBadge />

      <DropdownMenu>
        <DropdownMenuTrigger
          render={
            <Button variant="ghost" size="sm" className="gap-2">
              <div className="w-7 h-7 rounded-full bg-muted flex items-center justify-center">
                <UserIcon className="w-4 h-4" />
              </div>
              <span className="font-mono text-xs">{shortId}</span>
            </Button>
          }
        />
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>Signed in</DropdownMenuLabel>
          <DropdownMenuItem disabled>
            <span className="font-mono text-xs truncate">{userId ?? "—"}</span>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => logout("user")}>
            <LogOut className="w-4 h-4 mr-2" />
            Sign out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
