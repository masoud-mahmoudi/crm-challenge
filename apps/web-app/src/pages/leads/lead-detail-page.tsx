import { useEffect, useMemo } from 'react';
import { NetworkStatus } from '@apollo/client';
import { useQuery } from '@apollo/client/react';
import { ArrowLeft, Pencil, RefreshCw } from 'lucide-react';
import { Link, useLocation, useParams } from 'react-router-dom';

import { ActivityList } from '../../components/activities/ActivityList';
import { PageHeader } from '../../components/common/page-header';
import { PageState } from '../../components/common/page-state';
import { Alert, AlertDescription, AlertTitle } from '../../components/alert';
import { Badge } from '../../components/badge';
import { Button } from '../../components/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/card';
import { EnrichmentStatusBadge } from '../../components/leads/EnrichmentStatusBadge';
import { LeadStatusBadge } from '../../components/leads/LeadStatusBadge';
import { LEAD_DETAIL_QUERY } from '../../graphql/queries/leads';
import { usePendingLeadState } from '../../hooks/use-pending-lead-state';
import type { LeadDetailQueryData } from '../../types/crm';
import { formatDateTime, formatNullable, formatRelativeMinutes } from '../../utils/formatting';
import { buildLeadViewModel } from '../../utils/lead-view-model';

type DetailRouteState = {
  justCreated?: boolean;
  justUpdated?: boolean;
};

export function LeadDetailPage() {
  const { id } = useParams();
  const location = useLocation();
  const { getPendingSince, resolvePendingLead } = usePendingLeadState();
  const routeState = location.state as DetailRouteState | null;

  const { data, error, loading, networkStatus, refetch } = useQuery<LeadDetailQueryData>(LEAD_DETAIL_QUERY, {
    variables: { leadId: id as string },
    notifyOnNetworkStatusChange: true,
    pollInterval: import.meta.env.MODE === 'test' ? 0 : 5000,
    skip: !id,
  });

  useEffect(() => {
    if (id && (data?.activities.length ?? 0) > 0) {
      resolvePendingLead(id);
    }
  }, [data?.activities.length, id, resolvePendingLead]);

  const lead = useMemo(() => {
    if (!data?.lead) {
      return null;
    }

    return buildLeadViewModel({
      lead: data.lead,
      me: data.me,
      companies: data.companies,
      activities: data.activities,
      pendingSince: getPendingSince(data.lead.id),
    });
  }, [data, getPendingSince]);

  if (!id) {
    return (
      <PageState
        variant="error"
        title="Lead not found"
        description="The route is missing a lead identifier."
      />
    );
  }

  if (loading && !data) {
    return (
      <PageState
        variant="loading"
        title="Loading lead details"
        description="Fetching lead and activity information from GraphQL."
      />
    );
  }

  if (error && !data) {
    return (
      <PageState
        variant="error"
        title="Could not load the lead"
        description={error.message}
        actionLabel="Retry"
        onAction={() => {
          void refetch();
        }}
      />
    );
  }

  if (!data?.lead || !lead) {
    return (
      <PageState
        variant="empty"
        title="Lead unavailable"
        description="The gateway did not return a lead for this identifier."
      />
    );
  }

  const pendingSince = getPendingSince(lead.id);
  const showAsyncHint = routeState?.justCreated || lead.enrichmentStatus !== 'COMPLETED';

  return (
    <div className="grid gap-6">
      <PageHeader
        title={lead.name}
        description="Lead detail is polled every few seconds so asynchronous enrichment and follow-up activities become visible without a full reload."
        actions={
          <>
            <Button asChild type="button" variant="outline">
              <Link to="/leads">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to leads
              </Link>
            </Button>
            <Button onClick={() => void refetch()} type="button" variant="outline">
              <RefreshCw className={`mr-2 h-4 w-4 ${networkStatus === NetworkStatus.refetch ? 'animate-spin' : ''}`} />
              Refresh now
            </Button>
            <Button asChild type="button">
              <Link to={`/leads/${id}/edit`}>
                <Pencil className="mr-2 h-4 w-4" />
                Edit lead
              </Link>
            </Button>
          </>
        }
      />

      {routeState?.justUpdated ? (
        <Alert>
          <AlertTitle>Lead updated</AlertTitle>
          <AlertDescription>The latest lead changes were saved through GraphQL and the detail view has been refreshed.</AlertDescription>
        </Alert>
      ) : null}

      {showAsyncHint ? (
        <Alert>
          <AlertTitle>Eventual consistency in progress</AlertTitle>
          <AlertDescription>
            This page polls every 5 seconds. Newly created leads appear immediately, but enrichment can remain pending, score can stay blank, and follow-up activities may appear after later refresh cycles.
            {pendingSince ? ` Pending since ${formatRelativeMinutes(pendingSince)}.` : ''}
          </AlertDescription>
        </Alert>
      ) : null}

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-xl font-semibold">Lead details</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Name</p>
              <p className="mt-1 text-lg font-semibold">{lead.name}</p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Email</p>
              <p className="mt-1 text-lg font-semibold">{formatNullable(lead.email)}</p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Phone</p>
              <p className="mt-1 text-lg font-semibold">{formatNullable(lead.phone)}</p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Score</p>
              <p className="mt-1 text-lg font-semibold">{lead.score ?? '—'}</p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Company</p>
              <p className="mt-1 text-lg font-semibold">{formatNullable(lead.companyName)}</p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Owner</p>
              <p className="mt-1 text-lg font-semibold">{formatNullable(lead.ownerName)}</p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Created</p>
              <p className="mt-1 text-lg font-semibold">{formatDateTime(lead.createdAt)}</p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Updated</p>
              <p className="mt-1 text-lg font-semibold">{formatDateTime(lead.updatedAt)}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-xl font-semibold">Workflow state</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            <div className="flex flex-wrap gap-2">
              <LeadStatusBadge status={lead.status} />
              <EnrichmentStatusBadge status={lead.enrichmentStatus} />
              <Badge variant="outline">Polling every 5s</Badge>
            </div>
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Source</p>
              <p className="mt-1 font-medium">{formatNullable(lead.source)}</p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Description / notes</p>
              <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-foreground">
                {formatNullable(lead.description)}
              </p>
            </div>
          </CardContent>
        </Card>
      </section>

      <ActivityList activities={data.activities} />
    </div>
  );
}
