import { useState } from 'react';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider, useAuthContext } from './auth-context';
import type { MeResponse } from './types';

const authApiMock = vi.hoisted(() => ({
  login: vi.fn(),
  refresh: vi.fn(),
  me: vi.fn(),
  logout: vi.fn(),
}));

vi.mock('../services/api', () => ({
  authApi: authApiMock,
}));

const STORAGE_KEY = 'aerolytic.web-app.auth';

const mockMeResponse: MeResponse = {
  user: {
    id: 'user-1',
    email: 'ops-admin@aerialytic.io',
    full_name: 'Ops Admin',
    is_active: true,
    is_staff: true,
    created_at: '2026-03-25T10:00:00Z',
  },
  memberships: [
    {
      id: 'membership-1',
      role: 'admin',
      is_active: true,
      created_at: '2026-03-25T10:00:00Z',
      updated_at: '2026-03-25T10:00:00Z',
      company: {
        id: 'company-1',
        name: 'Aerolytic Holdings',
        company_type: 'CUSTOMER',
        parent_id: null,
        is_active: true,
        created_at: '2026-03-25T10:00:00Z',
        updated_at: '2026-03-25T10:00:00Z',
      },
    },
  ],
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

function SessionProbe() {
  const { loading, isAuthenticated, session, logout, refreshProfile } = useAuthContext();
  const [refreshError, setRefreshError] = useState<string | null>(null);

  return (
    <div>
      <div data-testid="loading">{loading ? 'loading' : 'idle'}</div>
      <div data-testid="authenticated">{isAuthenticated ? 'yes' : 'no'}</div>
      <div data-testid="user-email">{session?.user.email ?? 'none'}</div>
      <div data-testid="refresh-error">{refreshError ?? 'none'}</div>
      <button onClick={() => void logout()} type="button">
        Logout
      </button>
      <button
        onClick={async () => {
          try {
            await refreshProfile();
            setRefreshError(null);
          } catch (error) {
            setRefreshError(error instanceof Error ? error.message : 'Unknown refresh error');
          }
        }}
        type="button"
      >
        Refresh profile
      </button>
    </div>
  );
}

describe('AuthProvider', () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it('restores a session from a stored refresh token during bootstrap', async () => {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        accessToken: null,
        refreshToken: 'refresh-token-1',
        tokenType: 'Bearer',
        expiresAt: null,
      }),
    );

    authApiMock.refresh.mockResolvedValue({
      access_token: 'access-token-1',
      refresh_token: 'refresh-token-2',
      token_type: 'Bearer',
      expires_in: 3600,
    });
    authApiMock.me.mockResolvedValue(mockMeResponse);

    render(
      <AuthProvider>
        <SessionProbe />
      </AuthProvider>,
    );

    expect(screen.getByTestId('loading')).toHaveTextContent('loading');

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('idle');
      expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
      expect(screen.getByTestId('user-email')).toHaveTextContent('ops-admin@aerialytic.io');
    });

    expect(authApiMock.refresh).toHaveBeenCalledWith('refresh-token-1');
    expect(authApiMock.me).toHaveBeenCalledWith('access-token-1', 'Bearer');
    expect(JSON.parse(window.localStorage.getItem(STORAGE_KEY) ?? '{}')).toMatchObject({
      accessToken: 'access-token-1',
      refreshToken: 'refresh-token-2',
      tokenType: 'Bearer',
    });
  });

  it('clears the client session even when logout transport fails', async () => {
    const user = userEvent.setup();

    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        accessToken: 'access-token-1',
        refreshToken: 'refresh-token-1',
        tokenType: 'Bearer',
        expiresAt: Date.now() + 60000,
      }),
    );

    authApiMock.me.mockResolvedValue(mockMeResponse);
    authApiMock.logout.mockRejectedValue(new Error('Gateway unavailable'));

    render(
      <AuthProvider>
        <SessionProbe />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
    });

    await user.click(screen.getByRole('button', { name: 'Logout' }));

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('no');
      expect(screen.getByTestId('user-email')).toHaveTextContent('none');
    });

    expect(authApiMock.logout).toHaveBeenCalledWith('access-token-1', 'Bearer');
    expect(window.localStorage.getItem(STORAGE_KEY)).toBeNull();
  });

  it('clears the session and reports an expiry message when profile refresh fails', async () => {
    const user = userEvent.setup();

    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        accessToken: 'access-token-1',
        refreshToken: 'refresh-token-1',
        tokenType: 'Bearer',
        expiresAt: Date.now() + 60000,
      }),
    );

    authApiMock.me.mockResolvedValueOnce(mockMeResponse).mockRejectedValueOnce(new Error('Token expired'));

    render(
      <AuthProvider>
        <SessionProbe />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
    });

    await user.click(screen.getByRole('button', { name: 'Refresh profile' }));

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('no');
      expect(screen.getByTestId('refresh-error')).toHaveTextContent('Your session has expired. Please sign in again.');
    });

    expect(window.localStorage.getItem(STORAGE_KEY)).toBeNull();
  });
});
