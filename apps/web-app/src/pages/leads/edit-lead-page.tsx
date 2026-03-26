import { useMemo, useState } from 'react';
import { useMutation, useQuery } from '@apollo/client/react';
import { ArrowLeft } from 'lucide-react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import { PageHeader } from '../../components/common/page-header';
import { PageState } from '../../components/common/page-state';
import { isAuthFailureError, logoutPortal } from '../../auth/session-utils';
import { Button } from '../../components/button';
import { LeadForm } from '../../components/leads/LeadForm';
import { UPDATE_LEAD_MUTATION } from '../../graphql/mutations/leads';
import { DASHBOARD_QUERY } from '../../graphql/queries/dashboard';
import { LEAD_DETAIL_QUERY, LEADS_PAGE_QUERY } from '../../graphql/queries/leads';
import type {
  LeadFormValues,
  LeadDetailQueryData,
  UpdateLeadMutationData,
  UpdateLeadMutationVariables,
} from '../../types/crm';
import { buildLeadViewModel } from '../../utils/lead-view-model';

export function EditLeadPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { data, error, loading, refetch } = useQuery<LeadDetailQueryData>(LEAD_DETAIL_QUERY, {
    variables: { leadId: id as string },
    skip: !id,
  });

  const [updateLead, { loading: submitting }] = useMutation<
    UpdateLeadMutationData,
    UpdateLeadMutationVariables
  >(UPDATE_LEAD_MUTATION, {
    refetchQueries: id
      ? [
          { query: LEAD_DETAIL_QUERY, variables: { leadId: id } },
          { query: LEADS_PAGE_QUERY },
          { query: DASHBOARD_QUERY },
        ]
      : [{ query: LEADS_PAGE_QUERY }, { query: DASHBOARD_QUERY }],
  });

  const ownerOptions = useMemo(() => {
    if (!data?.me.user.id) {
      return [];
    }

    return [
      {
        id: data.me.user.id,
        label: data.me.user.fullName || data.me.user.email,
      },
    ];
  }, [data?.me.user.email, data?.me.user.fullName, data?.me.user.id]);

  const lead = useMemo(() => {
    if (!data?.lead) {
      return null;
    }

    return buildLeadViewModel({
      lead: data.lead,
      me: data.me,
      companies: data.companies,
      activities: data.activities,
    });
  }, [data]);

  const handleSubmit = async (values: LeadFormValues) => {
    if (!id) {
      return;
    }

    setSubmitError(null);

    try {
      const response = await updateLead({
        variables: {
          leadId: id,
          input: {
            name: values.name,
            title: values.name,
            email: values.email,
            phone: values.phone ?? null,
            source: values.source ?? null,
            status: values.status ?? null,
          },
        },
      });

      const updatedLead = response.data?.updateLead;
      if (!updatedLead) {
        throw new Error('The gateway did not return the updated lead.');
      }

      navigate(`/leads/${updatedLead.id}`, { replace: true, state: { justUpdated: true } });
    } catch (mutationError) {
      if (isAuthFailureError(mutationError)) {
        logoutPortal();
        return;
      }

      setSubmitError(mutationError instanceof Error ? mutationError.message : 'Unable to update lead.');
    }
  };

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
        title="Loading lead"
        description="Fetching lead details before editing."
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

  return (
    <div className="grid gap-6">
      <PageHeader
        title={`Edit ${lead.name}`}
        description="Update a lead through GraphQL. List and detail screens will refresh after the mutation completes."
        actions={
          <Button asChild type="button" variant="outline">
            <Link to={`/leads/${id}`}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to lead
            </Link>
          </Button>
        }
      />
      <LeadForm
        companies={data.companies}
        initialValues={{
          companyId: lead.companyId ?? undefined,
          name: lead.name,
          email: lead.email ?? '',
          phone: lead.phone ?? '',
          ownerUserId: lead.ownerUserId ?? undefined,
          source: lead.source ?? 'web-app',
          status: lead.status,
        }}
        mode="edit"
        onSubmit={handleSubmit}
        owners={ownerOptions}
        submitError={submitError}
        submitting={submitting}
      />
    </div>
  );
}