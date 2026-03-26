export interface GraphqlCompany {
  __typename?: 'Company';
  id: string;
  name: string;
  companyType: string;
  parentId?: string | null;
  isActive: boolean;
  createdAt?: string | null;
  updatedAt?: string | null;
}

export interface GraphqlUser {
  __typename?: 'User';
  id: string;
  email: string;
  fullName?: string | null;
  isActive?: boolean;
  isStaff?: boolean;
  createdAt?: string | null;
}

export interface GraphqlMembership {
  __typename?: 'Membership';
  id: string;
  role: string;
  isActive: boolean;
  company: GraphqlCompany;
  createdAt?: string | null;
  updatedAt?: string | null;
}

export interface GraphqlMe {
  __typename?: 'MePayload';
  user: GraphqlUser;
  memberships: GraphqlMembership[];
  accessibleCompanies: GraphqlCompany[];
}

export interface GraphqlLead {
  __typename?: 'Lead';
  id: string;
  title: string;
  name?: string | null;
  status: string;
  companyId?: string | null;
  ownerUserId?: string | null;
  source?: string | null;
  description?: string | null;
  email?: string | null;
  phone?: string | null;
  enrichmentStatus?: string | null;
  score?: number | null;
  createdAt?: string | null;
  updatedAt?: string | null;
}

export interface GraphqlActivity {
  __typename?: 'Activity';
  id: string;
  type: string;
  summary: string;
  leadId?: string | null;
  createdAt?: string | null;
}

export interface DashboardQueryData {
  me: GraphqlMe;
  companies: GraphqlCompany[];
  leads: GraphqlLead[];
}

export interface LeadsPageQueryData {
  me: GraphqlMe;
  companies: GraphqlCompany[];
  leads: GraphqlLead[];
}

export interface LeadDetailQueryData {
  me: GraphqlMe;
  companies: GraphqlCompany[];
  lead: GraphqlLead;
  activities: GraphqlActivity[];
}

export interface CreateLeadFormQueryData {
  me: GraphqlMe;
  companies: GraphqlCompany[];
}

export interface LeadFormValues {
  companyId?: string;
  name: string;
  email: string;
  phone?: string;
  ownerUserId?: string;
  source?: string;
  status?: string;
}

export interface CreateLeadInput extends LeadFormValues {
  companyId: string;
}

export interface UpdateLeadInput extends LeadFormValues {}

export interface CreateLeadMutationData {
  createLead: GraphqlLead;
}

export interface CreateLeadMutationVariables {
  input: {
    name?: string | null;
    title: string;
    companyId: string;
    email?: string | null;
    phone?: string | null;
    ownerUserId?: string | null;
    source?: string | null;
  };
}

export interface UpdateLeadMutationData {
  updateLead: GraphqlLead;
}

export interface UpdateLeadMutationVariables {
  leadId: string;
  input: {
    name?: string | null;
    title?: string | null;
    email?: string | null;
    phone?: string | null;
    source?: string | null;
    status?: string | null;
  };
}

export type EnrichmentStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED';

export interface LeadViewModel {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  status: string;
  enrichmentStatus: EnrichmentStatus;
  score: number | null;
  companyId: string | null;
  companyName: string | null;
  ownerUserId: string | null;
  ownerName: string | null;
  source: string | null;
  description: string | null;
  createdAt: string | null;
  updatedAt: string | null;
}
