import { useCallback, useState } from "react";
import {
  Activity,
  Calendar,
  FileText,
  LayoutDashboard,
  LogOut,
  Settings,
  Truck,
  Users,
  Zap,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react";
import { cn } from "../utils";

export type AdminNavItem = {
  label: string;
  to: string;
};

export type AdminNavSection = {
  title?: string;
  items: AdminNavItem[];
};

interface AdminSidebarProps {
  sections?: AdminNavSection[];
  items?: AdminNavItem[];
  activePath: string;
  onNavigate?: (path: string) => void;
  companyName?: string;
  onSignOut?: () => Promise<void> | void;
}

export function AdminSidebar({ sections, items = [], activePath, onNavigate, companyName, onSignOut }: AdminSidebarProps) {
  const displayCompanyName = companyName || "Account";
  const [collapsed, setCollapsed] = useState(false);
  const navSections = (sections && sections.length > 0 ? sections : [{ items }]).filter(
    (section) => section.items && section.items.length > 0,
  );

  const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
    dashboard: LayoutDashboard,
    leads: Users,
    fleet: Truck,
    operations: Activity,
    logs: FileText,
    // billing: CreditCard,
    scheduling: Calendar,
    settings: Settings,
  };

  const handleSignOut = useCallback(async () => {
    await onSignOut?.();
    onNavigate?.("/auth/login");
  }, [onNavigate, onSignOut]);

  return (
    <aside
      className={cn(
        "relative z-30 border-r bg-background flex flex-col h-screen sticky top-0 transition-[width] duration-200 ease-in-out",
        collapsed ? "w-16" : "w-64",
      )}
    >
      {/* Company Logo & Name */}
      <div className={cn("relative px-3 py-4 border-b min-h-[80px]", collapsed ? "px-2" : "px-6")}> 
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <Zap className="h-6 w-6 text-primary-foreground" />
          </div>
          <div className={cn("transition-opacity", collapsed && "opacity-0 pointer-events-none hidden")}> 
            <h2 className="font-semibold">Aerialytic</h2>
            <p className="text-xs text-muted-foreground">CRM workspace</p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => setCollapsed((v) => !v)}
          className="absolute -bottom-4 right-0 translate-x-1/2 z-40 inline-flex h-9 w-9 items-center justify-center rounded-full border bg-background shadow-sm text-muted-foreground hover:text-foreground hover:border-foreground/60 transition-colors"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronsRight className="h-4 w-4" /> : <ChevronsLeft className="h-4 w-4" />}
        </button>
      </div>

      {/* Navigation Menu */}
      <nav className={cn("flex-1 space-y-4", collapsed ? "p-2" : "p-4")}> 
        {navSections.map((section, sectionIndex) => (
          <div key={section.title ?? sectionIndex} className="space-y-1">
            {!collapsed && section.title ? (
              <h3 className="text-xs font-semibold text-muted-foreground mb-2 px-3">
                {section.title}
              </h3>
            ) : null}
            {section.items.map((item) => {
              const key = item.label.toLowerCase();
              const Icon = iconMap[key] ?? LayoutDashboard;
              const isActive =
                activePath === item.to || (item.to !== "/" && activePath.startsWith(`${item.to}/`));

              return (
                <button
                  key={item.to}
                  onClick={() => onNavigate?.(item.to)}
                  className={cn(
                    "flex w-full items-center gap-3 rounded-lg px-3 py-3 transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                    collapsed && "justify-center",
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <span className={cn("transition-opacity", collapsed && "sr-only")}>{item.label}</span>
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Account / Sign out */}
      <div className={cn("p-4 border-t", collapsed && "p-3")}> 
        <button
          onClick={handleSignOut}
          className="w-full"
        >
          <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors">
            <div className="flex items-center gap-3">
              <LogOut className="h-5 w-5 text-muted-foreground" />
              <div className={cn("text-left", collapsed && "sr-only")}> 
                <p className="text-sm font-medium">Log out</p>
                <p className="text-xs text-muted-foreground truncate">{displayCompanyName}</p>
              </div>
            </div>
          </div>
        </button>
      </div>
    </aside>
  );
}
