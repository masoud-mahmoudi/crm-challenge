import type { PropsWithChildren, ReactElement } from 'react';
import { render } from '@testing-library/react';
import type { MockedResponse } from '@apollo/client/testing';
import { MockedProvider } from '@apollo/client/testing/react';
import { MemoryRouter } from 'react-router-dom';

import { AuthContext, type AuthContextValue } from '../auth/auth-context';
import type { AuthSession } from '../auth/types';

export const mockSession: AuthSession = {
  accessToken: 'test-token',
  refreshToken: 'refresh-token',
  tokenType: 'Bearer',
  expiresAt: Date.now() + 60_000,
  user: {
    id: 'user-1',
    email: 'ops-admin@aerolytic.io',
    full_name: 'Ops Admin',
    is_active: true,
    is_staff: true,
    created_at: '2026-03-25T10:00:00Z',
    memberships: [],
  },
  memberships: [],
  accessible_companies: [
    {
      id: 'company-1',
      name: 'Aerolytic Holdings',
      company_type: 'CUSTOMER',
      parent_id: null,
      is_active: true,
      created_at: '2026-03-25T10:00:00Z',
      updated_at: '2026-03-25T10:00:00Z',
    },
  ],
};

export const mockAuthValue: AuthContextValue = {
  session: mockSession,
  loading: false,
  isAuthenticated: true,
  login: async () => undefined,
  logout: async () => undefined,
  refreshProfile: async () => undefined,
};

interface RenderWithProvidersOptions {
  route?: string;
  mocks?: MockedResponse[];
  authValue?: AuthContextValue;
}

function Wrapper({ children, authValue = mockAuthValue, mocks = [], route = '/' }: PropsWithChildren<RenderWithProvidersOptions>) {
  return (
    <MockedProvider mocks={mocks}>
      <AuthContext.Provider value={authValue}>
        <MemoryRouter initialEntries={[route]}>{children}</MemoryRouter>
      </AuthContext.Provider>
    </MockedProvider>
  );
}

export function renderWithProviders(ui: ReactElement, options: RenderWithProvidersOptions = {}) {
  return render(
    <Wrapper authValue={options.authValue} mocks={options.mocks} route={options.route}>
      {ui}
    </Wrapper>,
  );
}
