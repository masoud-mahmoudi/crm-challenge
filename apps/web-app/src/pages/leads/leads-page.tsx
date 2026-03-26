import { useMemo } from 'react';
import { NetworkStatus } from '@apollo/client';
import { useQuery } from '@apollo/client/react';
import { PlusCircle, RefreshCw } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

import { PageHeader } from '../../components/common/page-header';
import { PageState } from '../../components/common/page-state';
import { Button } from '../../components/button';
import { Card, CardContent } from '../../components/card';
import { LeadTable } from '../../components/leads/LeadTable';
import { LEADS_PAGE_QUERY } from '../../graphql/queries/leads';
import { usePendingLeadState } from '../../hooks/use-pending-lead-state';
import type { LeadsPageQueryData } from '../../types/crm';
import { buildLeadViewModel } from '../../utils/lead-view-model';

export function LeadsPage() {
  const navigate = useNavigate();
  const { getPendingSince } = usePendingLeadState();
  const { data, error, loading, networkStatus, refetch } = useQuery<LeadsPageQueryData>(LEADS_PAGE_QUERY, {
    notifyOnNetworkStatusChange: true,
  });

  const leads = useMemo(() => {
    if (!data) {
      return [];
    }

    return data.leads.map((lead) =>
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
        title="Loading leads"
        description="Fetching lead records from the GraphQL API."
      />
    );
  }

  if (error && !data) {
    return (
      <PageState
        variant="error"
        title="Could not load leads"
        description={error.message}
        actionLabel="Retry"
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
        title="Leads"
        description="Review your CRM pipeline, inspect enrichment progress, and open a lead to watch eventual consistency updates arrive."
        actions={
          <>
            <Button onClick={() => void refetch()} type="button" variant="outline">
              <RefreshCw className={`mr-2 h-4 w-4 ${networkStatus === NetworkStatus.refetch ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button asChild>
              <Link to="/leads/new">
                <PlusCircle className="mr-2 h-4 w-4" />
                Create Lead
              </Link>
            </Button>
          </>
        }
      />

      <Card className="shadow-sm">
        <CardContent className="pt-6 text-sm text-muted-foreground">
          Leads created from this UI appear immediately, but enrichment stays asynchronous. A newly created lead can show pending enrichment, no score, and no follow-up activities until later refresh or polling updates arrive.
        </CardContent>
      </Card>

      {leads.length === 0 ? (
        <PageState
          variant="empty"
          title="No leads yet"
          description="Create your first lead to start populating the CRM workspace."
          actionLabel="Create lead"
          onAction={() => navigate('/leads/new')}
        />
      ) : (
        <LeadTable leads={leads} isRefreshing={networkStatus === NetworkStatus.refetch} />
      )}
    </div>
  );
}
