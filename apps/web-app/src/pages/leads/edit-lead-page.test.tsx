import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { MockedResponse } from '@apollo/client/testing';
import { Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { UPDATE_LEAD_MUTATION } from '../../graphql/mutations/leads';
import { DASHBOARD_QUERY } from '../../graphql/queries/dashboard';
import { LEAD_DETAIL_QUERY, LEADS_PAGE_QUERY } from '../../graphql/queries/leads';
import { mockActivities, mockCompanies, mockLead, mockMe } from '../../test/graphql-mocks';
import { renderWithProviders } from '../../test/test-utils';
import { EditLeadPage } from './edit-lead-page';
import { LeadDetailPage } from './lead-detail-page';

const updatedLead = {
  ...mockLead,
  status: 'CONTACTED',
  source: 'sales-call',
  phone: '+1 555 010 9898',
  enrichmentStatus: 'COMPLETED',
  score: 88,
};

describe('EditLeadPage', () => {
  it('updates a lead and routes back to the detail page', async () => {
    const user = userEvent.setup();

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
            activities: mockActivities,
          },
        },
      },
      {
        request: {
          query: UPDATE_LEAD_MUTATION,
          variables: {
            leadId: 'lead-1',
            input: {
              name: 'Jordan Lee',
              title: 'Jordan Lee',
              email: 'jordan@example.com',
              phone: '+1 555 010 9898',
              source: 'sales-call',
              status: 'CONTACTED',
            },
          },
        },
        result: {
          data: {
            updateLead: updatedLead,
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
            lead: updatedLead,
            activities: mockActivities,
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
            leads: [updatedLead],
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
            leads: [updatedLead],
          },
        },
      },
    ];

    renderWithProviders(
      <Routes>
        <Route element={<EditLeadPage />} path="/leads/:id/edit" />
        <Route element={<LeadDetailPage />} path="/leads/:id" />
      </Routes>,
      {
        route: '/leads/lead-1/edit',
        mocks,
      },
    );

    expect(await screen.findByText('Update lead', { selector: 'h4' })).toBeInTheDocument();

    const phoneInput = screen.getByLabelText('Phone');
    await user.clear(phoneInput);
    await user.type(phoneInput, '+1 555 010 9898');

    await user.selectOptions(screen.getByLabelText('Status'), 'CONTACTED');
    const sourceInput = screen.getByLabelText('Source');
    await user.clear(sourceInput);
    await user.type(sourceInput, 'sales-call');

    await user.click(screen.getByRole('button', { name: 'Save changes' }));

    expect(await screen.findByText('Lead updated')).toBeInTheDocument();
    expect(await screen.findByText('CONTACTED')).toBeInTheDocument();
  });
});