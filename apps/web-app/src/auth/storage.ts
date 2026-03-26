import type { AuthTokens } from './types';

const STORAGE_KEY = 'aerolytic.web-app.auth';

const emptyTokens: AuthTokens = {
  accessToken: null,
  refreshToken: null,
  tokenType: 'Bearer',
  expiresAt: null,
};

export function loadStoredTokens(): AuthTokens {
  if (typeof window === 'undefined') {
    return emptyTokens;
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return emptyTokens;
  }

  try {
    const parsed = JSON.parse(raw) as Partial<AuthTokens>;
    return {
      accessToken: parsed.accessToken ?? null,
      refreshToken: parsed.refreshToken ?? null,
      tokenType: parsed.tokenType ?? 'Bearer',
      expiresAt: parsed.expiresAt ?? null,
    };
  } catch {
    window.localStorage.removeItem(STORAGE_KEY);
    return emptyTokens;
  }
}

export function storeTokens(tokens: AuthTokens) {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens));
}

export function clearStoredTokens() {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.removeItem(STORAGE_KEY);
}
