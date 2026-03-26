import { gql } from '@apollo/client';

export const LEAD_FIELDS = gql`
  fragment LeadFields on Lead {
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
`;
