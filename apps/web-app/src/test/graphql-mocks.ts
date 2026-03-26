import type { GraphqlActivity, GraphqlCompany, GraphqlLead, GraphqlMe } from '../types/crm';

export const mockCompanies: GraphqlCompany[] = [
  {
    __typename: 'Company',
    id: 'company-1',
    name: 'Aerolytic Holdings',
    companyType: 'CUSTOMER',
    parentId: null,
    isActive: true,
    createdAt: '2026-03-25T10:00:00Z',
    updatedAt: '2026-03-25T10:00:00Z',
  },
];

export const mockMe: GraphqlMe = {
  __typename: 'MePayload',
  user: {
    __typename: 'User',
    id: 'user-1',
    email: 'ops-admin@aerolytic.io',
    fullName: 'Ops Admin',
    isActive: true,
    isStaff: true,
    createdAt: '2026-03-25T10:00:00Z',
  },
  memberships: [
    {
      __typename: 'Membership',
      id: 'membership-1',
      role: 'admin',
      isActive: true,
      createdAt: '2026-03-25T10:00:00Z',
      updatedAt: '2026-03-25T10:00:00Z',
      company: mockCompanies[0],
    },
  ],
  accessibleCompanies: mockCompanies,
};

export const mockLead: GraphqlLead = {
  __typename: 'Lead',
  id: 'lead-1',
  title: 'Jordan Lee',
  name: 'Jordan Lee',
  status: 'NEW',
  companyId: 'company-1',
  ownerUserId: 'user-1',
  source: 'web-app',
  description: 'Created from the CRM frontend.',
  email: 'jordan@example.com',
  phone: '+1 555 010 0101',
  enrichmentStatus: 'PENDING',
  score: null,
  createdAt: '2026-03-25T10:00:00Z',
  updatedAt: '2026-03-25T10:00:00Z',
};

export const mockActivities: GraphqlActivity[] = [
  {
    __typename: 'Activity',
    id: 'activity-1',
    type: 'FOLLOW_UP',
    summary: 'Call scheduled',
    leadId: 'lead-1',
    createdAt: '2026-03-25T10:10:00Z',
  },
];
