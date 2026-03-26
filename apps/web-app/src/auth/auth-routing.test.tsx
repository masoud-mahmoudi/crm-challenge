import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';

import { ProtectedRoute } from './ProtectedRoute';
import { AuthContext, type AuthContextValue } from './auth-context';
import { AuthLayout } from './AuthLayout';
import { LoginPage } from './LoginPage';

function renderWithAuth(ui: React.ReactNode, authValue: AuthContextValue, initialEntries: Array<string | { pathname: string; state?: unknown }> = ['/']) {
  return render(
    <AuthContext.Provider value={authValue}>
      <MemoryRouter initialEntries={initialEntries}>{ui}</MemoryRouter>
    </AuthContext.Provider>,
  );
}

function LocationStateProbe() {
  const location = useLocation();
  const state = location.state as { from?: { pathname?: string } } | null;

  return (
    <div>
      <div data-testid="pathname">{location.pathname}</div>
      <div data-testid="from-pathname">{state?.from?.pathname ?? 'none'}</div>
    </div>
  );
}

describe('authentication routing', () => {
  it('redirects unauthenticated users from protected routes to the login page', async () => {
    renderWithAuth(
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route element={<div>Leads workspace</div>} path="/leads" />
        </Route>
        <Route element={<LocationStateProbe />} path="/auth/login" />
      </Routes>,
      {
        session: null,
        loading: false,
        isAuthenticated: false,
        login: vi.fn(),
        logout: vi.fn(),
        refreshProfile: vi.fn(),
      },
      ['/leads'],
    );

    expect(await screen.findByTestId('pathname')).toHaveTextContent('/auth/login');
    expect(screen.getByTestId('from-pathname')).toHaveTextContent('/leads');
  });

  it('submits the login form and navigates to the requested route', async () => {
    const user = userEvent.setup();
    const login = vi.fn().mockResolvedValue(undefined);

    renderWithAuth(
      <Routes>
        <Route element={<LoginPage />} path="/auth/login" />
        <Route element={<div>Leads workspace</div>} path="/leads" />
      </Routes>,
      {
        session: null,
        loading: false,
        isAuthenticated: false,
        login,
        logout: vi.fn(),
        refreshProfile: vi.fn(),
      },
      [{ pathname: '/auth/login', state: { from: { pathname: '/leads' } } }],
    );

    await user.clear(screen.getByLabelText('Email'));
    await user.type(screen.getByLabelText('Email'), 'ops-admin@aerialytic.io');
    await user.clear(screen.getByLabelText('Password'));
    await user.type(screen.getByLabelText('Password'), 'password123');
    await user.click(screen.getByRole('button', { name: 'Sign in' }));

    expect(login).toHaveBeenCalledWith({
      email: 'ops-admin@aerialytic.io',
      password: 'password123',
    });
    expect(await screen.findByText('Leads workspace')).toBeInTheDocument();
  });

  it('shows a sign-in error when login fails', async () => {
    const user = userEvent.setup();
    const login = vi.fn().mockRejectedValue(new Error('Invalid credentials'));

    renderWithAuth(
      <Routes>
        <Route element={<LoginPage />} path="/auth/login" />
      </Routes>,
      {
        session: null,
        loading: false,
        isAuthenticated: false,
        login,
        logout: vi.fn(),
        refreshProfile: vi.fn(),
      },
      ['/auth/login'],
    );

    await user.click(screen.getByRole('button', { name: 'Sign in' }));

    expect(await screen.findByText('Sign-in failed')).toBeInTheDocument();
    expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
  });

  it('redirects authenticated users away from the auth layout', async () => {
    renderWithAuth(
      <Routes>
        <Route element={<AuthLayout />} path="/auth/*" />
        <Route element={<div>Dashboard home</div>} path="/" />
      </Routes>,
      {
        session: {
          accessToken: 'access-token-1',
          refreshToken: 'refresh-token-1',
          tokenType: 'Bearer',
          expiresAt: Date.now() + 60000,
          user: {
            id: 'user-1',
            email: 'ops-admin@aerialytic.io',
            full_name: 'Ops Admin',
            is_active: true,
            is_staff: true,
            created_at: '2026-03-25T10:00:00Z',
          },
          memberships: [],
          accessible_companies: [],
        },
        loading: false,
        isAuthenticated: true,
        login: vi.fn(),
        logout: vi.fn(),
        refreshProfile: vi.fn(),
      },
      ['/auth/login'],
    );

    expect(await screen.findByText('Dashboard home')).toBeInTheDocument();
  });
});
