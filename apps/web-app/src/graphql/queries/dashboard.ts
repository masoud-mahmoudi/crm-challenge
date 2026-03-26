import { gql } from '@apollo/client';

import { COMPANY_FIELDS } from '../fragments/company';
import { LEAD_FIELDS } from '../fragments/lead';
import { USER_FIELDS } from '../fragments/user';

export const DASHBOARD_QUERY = gql`
  query DashboardPageData {
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
    leads {
      ...LeadFields
    }
  }
  ${USER_FIELDS}
  ${COMPANY_FIELDS}
  ${LEAD_FIELDS}
`;
