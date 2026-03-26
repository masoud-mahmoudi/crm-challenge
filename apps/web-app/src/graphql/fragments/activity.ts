import { gql } from '@apollo/client';

export const ACTIVITY_FIELDS = gql`
  fragment ActivityFields on Activity {
    id
    type
    summary
    leadId
    createdAt
  }
`;
