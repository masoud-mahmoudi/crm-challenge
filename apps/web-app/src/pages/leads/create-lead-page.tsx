import { useMemo, useState } from 'react';
import { useMutation, useQuery } from '@apollo/client/react';
import { ArrowLeft } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

import { PageHeader } from '../../components/common/page-header';
import { PageState } from '../../components/common/page-state';
import { isAuthFailureError, logoutPortal } from '../../auth/session-utils';
import { Button } from '../../components/button';
import { LeadForm } from '../../components/leads/LeadForm';
import { CREATE_LEAD_MUTATION } from '../../graphql/mutations/leads';
import { DASHBOARD_QUERY } from '../../graphql/queries/dashboard';
import { CREATE_LEAD_FORM_QUERY, LEADS_PAGE_QUERY } from '../../graphql/queries/leads';
import { usePendingLeadState } from '../../hooks/use-pending-lead-state';
import type {
  CreateLeadFormQueryData,
  LeadFormValues,
  CreateLeadMutationData,
  CreateLeadMutationVariables,
} from '../../types/crm';

export function CreateLeadPage() {
  const navigate = useNavigate();
  const { markLeadPending } = usePendingLeadState();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { data, error, loading, refetch } = useQuery<CreateLeadFormQueryData>(CREATE_LEAD_FORM_QUERY);
  const [createLead, { loading: submitting }] = useMutation<
    CreateLeadMutationData,
    CreateLeadMutationVariables
  >(CREATE_LEAD_MUTATION, {
    refetchQueries: [{ query: LEADS_PAGE_QUERY }, { query: DASHBOARD_QUERY }],
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

  const handleSubmit = async (values: LeadFormValues) => {
    setSubmitError(null);

    if (!values.companyId) {
      setSubmitError('A company is required to create a lead.');
      return;
    }

    try {
      const response = await createLead({
        variables: {
          input: {
            name: values.name,
            title: values.name,
            companyId: values.companyId,
            email: values.email,
            phone: values.phone ?? null,
            ownerUserId: values.ownerUserId ?? null,
            source: values.source ?? 'web-app',
          },
        },
      });

      const createdLead = response.data?.createLead;
      if (!createdLead) {
        throw new Error('The gateway did not return the created lead.');
      }

      markLeadPending(createdLead.id);
      navigate(`/leads/${createdLead.id}`, { state: { justCreated: true } });
    } catch (mutationError) {
      if (isAuthFailureError(mutationError)) {
        logoutPortal();
        return;
      }

      setSubmitError(mutationError instanceof Error ? mutationError.message : 'Unable to create lead.');
    }
  };

  if (loading && !data) {
    return (
      <PageState
        variant="loading"
        title="Preparing lead form"
        description="Loading available companies and current user data."
      />
    );
  }

  if (error && !data) {
    return (
      <PageState
        variant="error"
        title="Could not load form data"
        description={error.message}
        actionLabel="Retry"
        onAction={() => {
          void refetch();
        }}
      />
    );
  }

  if (!data || data.companies.length === 0) {
    return (
      <PageState
        variant="empty"
        title="No companies available"
        description="A lead needs a company assignment before it can be created."
      />
    );
  }

  return (
    <div className="grid gap-6">
      <PageHeader
        title="Create lead"
        description="Submit a new lead through GraphQL. The detail page will poll for eventual consistency updates after creation."
        actions={
          <Button asChild type="button" variant="outline">
            <Link to="/leads">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to leads
            </Link>
          </Button>
        }
      />
      <LeadForm
        companies={data.companies}
        onSubmit={handleSubmit}
        owners={ownerOptions}
        submitError={submitError}
        submitting={submitting}
      />
    </div>
  );
}
