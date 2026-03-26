import { gql } from '@apollo/client';

import { ACTIVITY_FIELDS } from '../fragments/activity';
import { COMPANY_FIELDS } from '../fragments/company';
import { LEAD_FIELDS } from '../fragments/lead';
import { USER_FIELDS } from '../fragments/user';

export const LEADS_PAGE_QUERY = gql`
  query LeadsPageData {
    leads {
      id
    title
    name
    status
    companyId
    ownerUserId
    source
    description
    email
    phone
    enrichmentStatus
    score
    createdAt
    updatedAt
    }
  }
`;

export const LEAD_DETAIL_QUERY = gql`
  query LeadDetailPageData($leadId: String!) {
    me {
      user {
        ...UserFields
      }
      memberships {
        id
        role
        isActive
        createdAt
        updatedAt
        company {
          ...CompanyFields
        }
      }
      accessibleCompanies {
        ...CompanyFields
      }
    }
    companies {
      ...CompanyFields
    }
    lead(leadId: $leadId) {
      ...LeadFields
    }
    activities(leadId: $leadId) {
      ...ActivityFields
    }
  }
  ${USER_FIELDS}
  ${COMPANY_FIELDS}
  ${LEAD_FIELDS}
  ${ACTIVITY_FIELDS}
`;

export const CREATE_LEAD_FORM_QUERY = gql`
  query CreateLeadFormData {
    me {
      user {
        ...UserFields
      }
      memberships {
        id
        role
        isActive
        createdAt
        updatedAt
        company {
          ...CompanyFields
        }
      }
      accessibleCompanies {
        ...CompanyFields
      }
    }
    companies {
      ...CompanyFields
    }
  }
  ${USER_FIELDS}
  ${COMPANY_FIELDS}
`;
