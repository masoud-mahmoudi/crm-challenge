import { ApolloClient, HttpLink, InMemoryCache, from } from '@apollo/client';
import { CombinedGraphQLErrors } from '@apollo/client/errors';
import { setContext } from '@apollo/client/link/context';
import { onError } from '@apollo/client/link/error';

import { isAuthFailureError, logoutPortal } from '../auth/session-utils';
import { loadStoredTokens } from '../auth/storage';

const GRAPHQL_URL =
  (import.meta.env.VITE_GRAPHQL_URL as string | undefined)?.replace(/\/$/, '') ?? '/graphql';
const CSRF_COOKIE_NAME = 'csrftoken';
const CSRF_HEADER_NAME = 'X-CSRFToken';
const CSRF_BOOTSTRAP_QUERY = 'query IntrospectionQuery { __schema { queryType { name } } }';

let csrfBootstrapPromise: Promise<string | null> | null = null;

function readCookie(name: string) {
  if (typeof document === 'undefined') {
    return null;
  }

  const cookie = document.cookie
    .split(';')
    .map((part) => part.trim())
    .find((part) => part.startsWith(`${name}=`));

  if (!cookie) {
    return null;
  }

  return decodeURIComponent(cookie.slice(name.length + 1));
}

function buildCsrfBootstrapUrl(graphqlUrl: string) {
  const baseOrigin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost';
  const url = new URL(graphqlUrl, baseOrigin);
  url.searchParams.set('operationName', 'IntrospectionQuery');
  url.searchParams.set('query', CSRF_BOOTSTRAP_QUERY);
  return url.toString();
}

async function ensureCsrfToken(graphqlUrl: string) {
  const existingToken = readCookie(CSRF_COOKIE_NAME);
  if (existingToken) {
    return existingToken;
  }

  if (typeof fetch !== 'function') {
    return null;
  }

  if (!csrfBootstrapPromise) {
    csrfBootstrapPromise = fetch(buildCsrfBootstrapUrl(graphqlUrl), {
      method: 'GET',
      credentials: 'include',
      headers: {
        Accept: 'application/json',
      },
    })
      .then(() => readCookie(CSRF_COOKIE_NAME))
      .catch(() => null)
      .finally(() => {
        csrfBootstrapPromise = null;
      });
  }

  return csrfBootstrapPromise;
}

const authLink = setContext((_, context) => {
  const tokens = loadStoredTokens();

  return {
    headers: {
      ...context.headers,
      ...(tokens.accessToken
        ? {
            Authorization: `${tokens.tokenType || 'Bearer'} ${tokens.accessToken}`,
          }
        : {}),
    },
  };
});

const errorLink = onError(({ error }) => {
  const graphQlUnauthorized = CombinedGraphQLErrors.is(error)
    ? error.errors.some((graphqlError) => isAuthFailureError(graphqlError))
    : false;

  if (graphQlUnauthorized || isAuthFailureError(error)) {
    logoutPortal();
  }
});

const httpLink = new HttpLink({
  uri: GRAPHQL_URL,
  fetch: async (uri, options) => {
    const requestUrl = typeof uri === 'string' ? uri : uri.toString();
    const method = (options?.method ?? 'POST').toUpperCase();
    const headers = new Headers(options?.headers);

    if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
      const csrfToken = (await ensureCsrfToken(requestUrl)) ?? readCookie(CSRF_COOKIE_NAME);
      if (csrfToken && !headers.has(CSRF_HEADER_NAME)) {
        headers.set(CSRF_HEADER_NAME, csrfToken);
      }
    }

    return fetch(requestUrl, {
      ...options,
      headers,
      credentials: 'include',
    });
  },
});

export const apolloClient = new ApolloClient({
  link: from([errorLink, authLink, httpLink]),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          leads: {
            merge: (_, incoming: unknown[]) => incoming,
          },
          activities: {
            keyArgs: ['leadId'],
            merge: (_, incoming: unknown[]) => incoming,
          },
          companies: {
            merge: (_, incoming: unknown[]) => incoming,
          },
        },
      },
    },
  }),
  defaultOptions: {
    watchQuery: {
      fetchPolicy: 'cache-and-network',
      nextFetchPolicy: 'cache-first',
    },
    query: {
      fetchPolicy: 'network-only',
    },
  },
});