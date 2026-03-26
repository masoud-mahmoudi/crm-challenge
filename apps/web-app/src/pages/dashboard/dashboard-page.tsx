import { useMemo } from 'react';
import { NetworkStatus } from '@apollo/client';
import { useQuery } from '@apollo/client/react';
import { ArrowRight, BriefcaseBusiness, Building2, LayoutDashboard, PlusCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

import { StatsCard } from '../../components/admin/StatsCard';
import { PageHeader } from '../../components/common/page-header';
import { PageState } from '../../components/common/page-state';
import { Button } from '../../components/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/card';
import { LeadTable } from '../../components/leads/LeadTable';
import { DASHBOARD_QUERY } from '../../graphql/queries/dashboard';
import { usePendingLeadState } from '../../hooks/use-pending-lead-state';
import type { DashboardQueryData } from '../../types/crm';
import { buildLeadViewModel } from '../../utils/lead-view-model';

export function DashboardPage() {
  const { getPendingSince } = usePendingLeadState();
  const { data, error, loading, networkStatus, refetch } = useQuery<DashboardQueryData>(DASHBOARD_QUERY, {
    notifyOnNetworkStatusChange: true,
  });

  const recentLeads = useMemo(() => {
    if (!data) {
      return [];
    }

    return [...data.leads]
      .sort((left, right) => (right.createdAt || '').localeCompare(left.createdAt || ''))
      .slice(0, 5)
      .map((lead) =>
        buildLeadViewModel({
          lead,
          me: data.me,
          companies: data.companies,
          pendingSince: getPendingSince(lead.id),
        }),
      );
  }, [data, getPendingSince]);

  if (loading && !data) {
    return (
      <PageState
        variant="loading"
        title="Loading dashboard"
        description="Fetching CRM summary data from the GraphQL gateway."
      />
    );
  }

  if (error && !data) {
    return (
      <PageState
        variant="error"
        title="Could not load the dashboard"
        description={error.message}
        actionLabel="Try again"
        onAction={() => {
          void refetch();
        }}
      />
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="grid gap-6">
      <PageHeader
        title={`Welcome back${data.me.user.fullName ? `, ${data.me.user.fullName}` : ''}`}
        description="Use the CRM workspace to review recently created leads, navigate into lead details, and monitor enrichment progress."
        actions={
          <>
            <Button asChild variant="outline">
              <Link to="/leads">
                View all leads
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild>
              <Link to="/leads/new">
                <PlusCircle className="mr-2 h-4 w-4" />
                Create lead
              </Link>
            </Button>
          </>
        }
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatsCard
          title="Total leads"
          value={String(data.leads.length)}
          change="Loaded through GraphQL"
          trend="up"
          icon={LayoutDashboard}
        />
        <StatsCard
          title="Accessible companies"
          value={String(data.companies.length)}
          change="Available for lead creation"
          trend="up"
          icon={Building2}
        />
        <StatsCard
          title="Memberships"
          value={String(data.me.memberships.length)}
          change="Derived from current user context"
          trend="up"
          icon={BriefcaseBusiness}
        />
        <StatsCard
          title="Sync status"
          value={networkStatus === NetworkStatus.refetch ? 'Refreshing' : 'Live'}
          change="GraphQL cache and network"
          trend="up"
          icon={ArrowRight}
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <LeadTable leads={recentLeads} isRefreshing={networkStatus === NetworkStatus.refetch} />

        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-xl font-semibold">Quick navigation</CardTitle>
            <CardDescription>
              The frontend talks only to the API gateway. Business data comes from GraphQL, while auth and session remain on the existing REST flow.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            <Link className="rounded-2xl border border-border bg-card p-4 transition-colors hover:bg-muted/40" to="/leads">
              <p className="font-medium">Leads workspace</p>
              <p className="mt-1 text-sm text-muted-foreground">
                View pipeline state, loading/error states, and refresh data from the gateway.
              </p>
            </Link>
            <Link className="rounded-2xl border border-border bg-card p-4 transition-colors hover:bg-muted/40" to="/leads/new">
              <p className="font-medium">Create a lead</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Submit a new lead and follow its eventual consistency state on the detail page.
              </p>
            </Link>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
