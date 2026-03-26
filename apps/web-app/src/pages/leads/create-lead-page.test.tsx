import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { MockedResponse } from '@apollo/client/testing';
import { Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { CREATE_LEAD_MUTATION } from '../../graphql/mutations/leads';
import { DASHBOARD_QUERY } from '../../graphql/queries/dashboard';
import { CREATE_LEAD_FORM_QUERY, LEAD_DETAIL_QUERY, LEADS_PAGE_QUERY } from '../../graphql/queries/leads';
import { mockCompanies, mockMe } from '../../test/graphql-mocks';
import { renderWithProviders } from '../../test/test-utils';
import { CreateLeadPage } from './create-lead-page';
import { LeadDetailPage } from './lead-detail-page';

const createdLead = {
  __typename: 'Lead',
  id: 'lead-99',
  title: 'Taylor Brooks',
  name: 'Taylor Brooks',
  status: 'NEW',
  companyId: 'company-1',
  ownerUserId: 'user-1',
  source: 'web-app',
  description: null,
  email: 'taylor@example.com',
  phone: '+1 555 010 7777',
  enrichmentStatus: 'PENDING',
  score: null,
  createdAt: '2026-03-25T11:00:00Z',
  updatedAt: '2026-03-25T11:00:00Z',
};

describe('CreateLeadPage', () => {
  it('submits the form and navigates to the created lead detail page', async () => {
    const user = userEvent.setup();
    const mocks: MockedResponse[] = [
      {
        request: {
          query: CREATE_LEAD_FORM_QUERY,
        },
        result: {
          data: {
            me: mockMe,
            companies: mockCompanies,
          },
        },
      },
      {
        request: {
          query: DASHBOARD_QUERY,
        },
        result: {
          data: {
            me: mockMe,
            companies: mockCompanies,
            leads: [createdLead],
          },
        },
      },
      {
        request: {
          query: LEADS_PAGE_QUERY,
        },
        result: {
          data: {
            me: mockMe,
            companies: mockCompanies,
            leads: [createdLead],
          },
        },
      },
      {
        request: {
          query: CREATE_LEAD_MUTATION,
          variables: {
            input: {
              name: 'Taylor Brooks',
              title: 'Taylor Brooks',
              companyId: 'company-1',
              email: 'taylor@example.com',
              phone: '+1 555 010 7777',
              ownerUserId: null,
              source: 'web-app',
            },
          },
        },
        result: {
          data: {
            createLead: createdLead,
          },
        },
      },
      {
        request: {
          query: LEAD_DETAIL_QUERY,
          variables: {
            leadId: 'lead-99',
          },
        },
        result: {
          data: {
            me: mockMe,
            companies: mockCompanies,
            lead: createdLead,
            activities: [],
          },
        },
      },
    ];

    renderWithProviders(
      <Routes>
        <Route element={<CreateLeadPage />} path="/leads/new" />
        <Route element={<LeadDetailPage />} path="/leads/:id" />
      </Routes>,
      {
        route: '/leads/new',
        mocks,
      },
    );

    expect(await screen.findByText('Create lead', { selector: 'h1' })).toBeInTheDocument();

    await user.type(screen.getByLabelText('Name'), 'Taylor Brooks');
    await user.type(screen.getByLabelText('Email'), 'taylor@example.com');
    await user.type(screen.getByLabelText('Phone'), '+1 555 010 7777');
    await user.click(screen.getByRole('button', { name: 'Create lead' }));

    expect(await screen.findByText('Taylor Brooks', { selector: 'h1' })).toBeInTheDocument();
    expect(await screen.findByText('Pending enrichment')).toBeInTheDocument();
  });
});
