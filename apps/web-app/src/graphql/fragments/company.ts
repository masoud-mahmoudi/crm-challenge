import { gql } from '@apollo/client';

export const COMPANY_FIELDS = gql`
  fragment CompanyFields on Company {
    id
    name
    companyType
    parentId
    isActive
    createdAt
    updatedAt
  }
`;
