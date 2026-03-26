import { gql } from '@apollo/client';

import { LEAD_FIELDS } from '../fragments/lead';

export const CREATE_LEAD_MUTATION = gql`
  mutation CreateLead($input: CreateLeadInput!) {
    createLead(input: $input) {
      ...LeadFields
    }
  }
  ${LEAD_FIELDS}
`;

export const UPDATE_LEAD_MUTATION = gql`
  mutation UpdateLead($leadId: String!, $input: UpdateLeadInput!) {
    updateLead(leadId: $leadId, input: $input) {
      ...LeadFields
    }
  }
  ${LEAD_FIELDS}
`;
