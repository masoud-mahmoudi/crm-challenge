import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from 'react';

import { authApi } from '../services/api';
import { clearStoredTokens, loadStoredTokens, storeTokens } from './storage';
import type { AuthSession, AuthTokens, LoginCredentials, LoginResponse, MeResponse } from './types';

export type AuthContextValue = {
  session: AuthSession | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | null>(null);

function buildTokens(response: LoginResponse, previousRefreshToken?: string | null): AuthTokens {
  return {
    accessToken: response.access_token,
    refreshToken: response.refresh_token ?? previousRefreshToken ?? null,
    tokenType: response.token_type ?? 'Bearer',
    expiresAt: typeof response.expires_in === 'number' ? Date.now() + response.expires_in * 1000 : null,
  };
}

function mergeSession(tokens: AuthTokens, me: MeResponse): AuthSession {
  return {
    ...tokens,
    ...me,
  };
}

async function hydrateSession(tokens: AuthTokens): Promise<AuthSession> {
  if (!tokens.accessToken) {
    throw new Error('Missing access token');
  }

  const me = await authApi.me(tokens.accessToken, tokens.tokenType);
  return mergeSession(tokens, me);
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [loading, setLoading] = useState(true);

  const applySession = useCallback((nextSession: AuthSession | null) => {
    setSession(nextSession);
    if (nextSession) {
      storeTokens({
        accessToken: nextSession.accessToken,
        refreshToken: nextSession.refreshToken,
        tokenType: nextSession.tokenType,
        expiresAt: nextSession.expiresAt,
      });
    } else {
      clearStoredTokens();
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    const bootstrap = async () => {
      const storedTokens = loadStoredTokens();

      if (!storedTokens.accessToken && !storedTokens.refreshToken) {
        if (!cancelled) {
          setLoading(false);
        }
        return;
      }

      try {
        let activeTokens = storedTokens;

        if (!activeTokens.accessToken && activeTokens.refreshToken) {
          const refreshed = await authApi.refresh(activeTokens.refreshToken);
          activeTokens = buildTokens(refreshed, activeTokens.refreshToken);
        }

        const hydratedSession = await hydrateSession(activeTokens);
        if (!cancelled) {
          applySession(hydratedSession);
        }
      } catch {
        if (!cancelled) {
          applySession(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    void bootstrap();

    return () => {
      cancelled = true;
    };
  }, [applySession]);

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      const response = await authApi.login(credentials);
      const tokens = buildTokens(response, response.refresh_token ?? null);
      const nextSession = await hydrateSession(tokens);
      applySession(nextSession);
    },
    [applySession],
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout(session?.accessToken, session?.tokenType ?? 'Bearer');
    } catch {
      // ignore logout transport failures and clear client session regardless
    } finally {
      applySession(null);
    }
  }, [applySession, session?.accessToken, session?.tokenType]);

  const refreshProfile = useCallback(async () => {
    if (!session?.refreshToken && !session?.accessToken) {
      return;
    }

    let activeTokens: AuthTokens = {
      accessToken: session?.accessToken ?? null,
      refreshToken: session?.refreshToken ?? null,
      tokenType: session?.tokenType ?? 'Bearer',
      expiresAt: session?.expiresAt ?? null,
    };

    try {
      if (!activeTokens.accessToken && activeTokens.refreshToken) {
        const refreshed = await authApi.refresh(activeTokens.refreshToken);
        activeTokens = buildTokens(refreshed, activeTokens.refreshToken);
      }

      const nextSession = await hydrateSession(activeTokens);
      applySession(nextSession);
    } catch {
      applySession(null);
      throw new Error('Your session has expired. Please sign in again.');
    }
  }, [applySession, session?.accessToken, session?.expiresAt, session?.refreshToken, session?.tokenType]);

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      loading,
      isAuthenticated: Boolean(session?.accessToken),
      login,
      logout,
      refreshProfile,
    }),
    [session, loading, login, logout, refreshProfile],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used inside an AuthProvider.');
  }

  return context;
}
