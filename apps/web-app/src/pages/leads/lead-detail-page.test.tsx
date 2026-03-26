import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { MockedResponse } from '@apollo/client/testing';
import { Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import { LEAD_DETAIL_QUERY } from '../../graphql/queries/leads';
import { mockActivities, mockCompanies, mockLead, mockMe } from '../../test/graphql-mocks';
import { renderWithProviders } from '../../test/test-utils';
import { LeadDetailPage } from './lead-detail-page';

const pendingLeadStorageKey = 'aerolytic.web-app.pending-leads';

describe('LeadDetailPage', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('updates the eventual consistency state after a refresh returns new activities', async () => {
    const user = userEvent.setup();
    window.localStorage.setItem(pendingLeadStorageKey, JSON.stringify({ 'lead-1': Date.now() }));

    const mocks: MockedResponse[] = [
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
            activities: [],
          },
        },
      },
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
    ];

    renderWithProviders(
      <Routes>
        <Route element={<LeadDetailPage />} path="/leads/:id" />
      </Routes>,
      {
        route: '/leads/lead-1',
        mocks,
      },
    );

    expect(await screen.findByText('Jordan Lee', { selector: 'h1' })).toBeInTheDocument();
    expect(await screen.findByText('Pending enrichment')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Refresh now' }));

    expect(await screen.findByText('Completed')).toBeInTheDocument();
    expect(await screen.findByText('Call scheduled')).toBeInTheDocument();
  });
});
