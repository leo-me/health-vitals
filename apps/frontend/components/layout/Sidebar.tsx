"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Cpu,
  Activity,
  Bell,
  Plug,
  ActivityIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const NAV: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/devices", label: "Devices", icon: Cpu },
  { href: "/sensor-recordings", label: "Recordings", icon: Activity },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/adapters", label: "Adapters", icon: Plug },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-40 w-64 bg-sidebar text-sidebar-foreground flex flex-col">
      <div className="flex items-center gap-2 px-6 h-16 border-b border-sidebar-border">
        <div className="w-7 h-7 rounded-lg bg-vital flex items-center justify-center">
          <ActivityIcon className="w-4 h-4 text-vital-foreground" />
        </div>
        <span className="font-heading font-bold tracking-tight text-base">
          Sensors2Care
        </span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                active
                  ? "bg-sidebar-hover text-white"
                  : "text-sidebar-foreground/80 hover:bg-sidebar-hover hover:text-white",
              )}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="px-6 py-4 text-[10px] text-sidebar-foreground/50 border-t border-sidebar-border font-mono">
        Sensors2Care Admin · v0.1
      </div>
    </aside>
  );
}
