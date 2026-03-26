import type { PropsWithChildren } from 'react';
import { ApolloProvider } from '@apollo/client/react';

import { apolloClient } from '../graphql/apolloClient';

export function AppProviders({ children }: PropsWithChildren) {
  return <ApolloProvider client={apolloClient}>{children}</ApolloProvider>;
}