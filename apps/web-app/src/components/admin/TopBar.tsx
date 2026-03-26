import * as React from "react";
import { Bell, Menu, Zap } from "lucide-react";

import { Badge } from "../badge";

interface TopBarProps {
  title?: string;
  activeTab?: string;
  subtitle?: string;
  notificationCount?: number;
  onToggleMenu?: () => void;
  isMenuOpen?: boolean;
}

export function TopBar({
  title,
  activeTab,
  subtitle = "Mobile Charging Services Platform",
  notificationCount = 0,
  onToggleMenu,
  isMenuOpen,
}: TopBarProps) {
  const tabKey = (activeTab ?? title ?? "dashboard").toLowerCase();
  const descriptions: Record<string, string> = {
    dashboard: "Track CRM health and recent lead activity",
    leads: "Browse, create, and monitor CRM leads",
    fleet: "Manage your mobile units",
    operations: "Track daily operations",
    logs: "View system activity",
    billing: "Manage billing and payments",
    scheduling: "Organize service schedules",
    settings: "Configure your account",
  };

  return (
        <header className="border-b bg-background sticky top-0 z-10">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-xl capitalize">{activeTab ?? title ?? "dashboard"}</h1>
                <p className="text-sm text-muted-foreground">
                  {descriptions[tabKey] ?? subtitle}
                </p>
              </div>
              <div className="flex items-center gap-4">
                <div className="relative">
                  <Bell className="h-5 w-5 text-muted-foreground" />
                  <Badge className="absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center p-0 text-xs">
                    5
                  </Badge>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Last updated</p>
                  <p className="text-sm">2 min ago</p>
                </div>
              </div>
            </div>
          </div>
        </header>
  );
}
