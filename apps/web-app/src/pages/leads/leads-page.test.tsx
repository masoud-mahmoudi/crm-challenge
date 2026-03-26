import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { MockedResponse } from '@apollo/client/testing';
import { Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { LEAD_DETAIL_QUERY, LEADS_PAGE_QUERY } from '../../graphql/queries/leads';
import { mockActivities, mockCompanies, mockLead, mockMe } from '../../test/graphql-mocks';
import { renderWithProviders } from '../../test/test-utils';
import { LeadDetailPage } from './lead-detail-page';
import { LeadsPage } from './leads-page';

const leadsSuccessMock: MockedResponse = {
  request: {
    query: LEADS_PAGE_QUERY,
  },
  result: {
    data: {
      me: mockMe,
      companies: mockCompanies,
      leads: [mockLead],
    },
  },
};

describe('LeadsPage', () => {
  it('renders the leads route through the authenticated app routes', async () => {
    const user = userEvent.setup();

    renderWithProviders(
      <Routes>
        <Route element={<LeadsPage />} path="/leads" />
        <Route element={<LeadDetailPage />} path="/leads/:id" />
      </Routes>,
      {
        route: '/leads',
        mocks: [
          leadsSuccessMock,
          {
            request: {
              query: LEAD_DETAIL_QUERY,
              variables: {
                leadId: 'lead-1',
              },
            },
            result: {
              data: {
                me: mockMe,
                companies: mockCompanies,
                lead: mockLead,
                activities: mockActivities,
              },
            },
          },
        ],
      },
    );

    expect(await screen.findByRole('heading', { name: 'Leads' })).toBeInTheDocument();
    expect(await screen.findByText('Jordan Lee')).toBeInTheDocument();

    await user.click(screen.getByText('Jordan Lee'));

    expect(await screen.findByRole('heading', { name: 'Jordan Lee' })).toBeInTheDocument();
  });

  it('shows a loading state before the leads query resolves', () => {
    renderWithProviders(<LeadsPage />, {
      mocks: [
        {
          ...leadsSuccessMock,
          delay: 50,
        },
      ],
    });

    expect(screen.getByText('Loading leads')).toBeInTheDocument();
  });

  it('shows a friendly error state when the leads query fails', async () => {
    renderWithProviders(<LeadsPage />, {
      mocks: [
        {
          request: {
            query: LEADS_PAGE_QUERY,
          },
          error: new Error('Gateway unavailable'),
        },
      ],
    });

    expect(await screen.findByText('Could not load leads')).toBeInTheDocument();
    expect(await screen.findByText('Gateway unavailable')).toBeInTheDocument();
  });
});
