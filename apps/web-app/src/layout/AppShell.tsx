import { useMemo } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Building2, Mail, ShieldCheck } from 'lucide-react';

import { useAuth } from '../auth/useAuth';
import { AdminSidebar, type AdminNavItem } from '../components/admin/admin-sidebar';
import { TopBar } from '../components/admin/TopBar';
import { Badge } from '../components/badge';

const navItems: AdminNavItem[] = [
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Leads', to: '/leads' },
  { label: 'Settings', to: '/settings' },
];

export function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, session } = useAuth();

  const membershipCount = session?.memberships.length ?? 0;
  const companyCount = session?.accessible_companies.length ?? 0;
  const primaryCompany = session?.accessible_companies[0]?.name ?? 'Workspace';

  const activeTitle = useMemo(() => {
    const ordered = [...navItems].sort((a, b) => b.to.length - a.to.length);
    const match = ordered.find(
      (item) =>
        location.pathname === item.to || location.pathname.startsWith(`${item.to}/`)
    );
    return match?.label ?? 'Dashboard';
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen">
        <AdminSidebar
        items={navItems}
        activePath={location.pathname}
          onNavigate={navigate}
          companyName={primaryCompany}
          onSignOut={logout}
        />
        <div className="flex min-h-screen flex-1 flex-col bg-muted/35">
          <TopBar
            title="Aerolytic CRM"
            activeTab={activeTitle}
            subtitle="Authenticated CRM workflows backed by the API gateway"
            notificationCount={membershipCount}
          />
          <section className="border-b border-border bg-background/90 px-6 py-4 backdrop-blur">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Signed in as</p>
                <h2 className="text-xl font-semibold tracking-tight">
                  {session?.user.full_name ?? 'Unknown user'}
                </h2>
                <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                  <span className="inline-flex items-center gap-2">
                    <Mail className="h-4 w-4" />
                    {session?.user.email}
                  </span>
                  <span className="inline-flex items-center gap-2">
                    <Building2 className="h-4 w-4" />
                    {primaryCompany}
                  </span>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary" className="px-3 py-1 text-sm">
                  {companyCount} companies
                </Badge>
                <Badge variant="secondary" className="px-3 py-1 text-sm">
                  {membershipCount} memberships
                </Badge>
                <Badge variant="outline" className="px-3 py-1 text-sm">
                  <ShieldCheck className="mr-2 h-4 w-4" />
                  {session?.tokenType ?? 'Bearer'} session
                </Badge>
              </div>
            </div>
          </section>
          <main className="flex-1 p-6">
            <div className="mx-auto w-full max-w-7xl">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}