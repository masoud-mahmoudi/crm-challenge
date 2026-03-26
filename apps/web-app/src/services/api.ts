import type { LoginCredentials, LoginResponse, MeResponse } from '../auth/types';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '') ?? '';

type RequestOptions = RequestInit & {
  token?: string | null;
  tokenType?: string;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const hasBody = options.body !== undefined && options.body !== null;

  if (hasBody && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  if (options.token) {
    headers.set('Authorization', `${options.tokenType ?? 'Bearer'} ${options.token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get('content-type') ?? '';
  const isJson = contentType.includes('application/json');
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const message =
      typeof payload === 'object' && payload !== null
        ? ((payload as { detail?: string; message?: string }).detail ??
          (payload as { detail?: string; message?: string }).message ??
          response.statusText)
        : response.statusText;

    throw new Error(message || 'Request failed');
  }

  return payload as T;
}

export const authApi = {
  login(credentials: LoginCredentials) {
    return request<LoginResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },
  refresh(refreshToken: string) {
    return request<LoginResponse>('/api/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  },
  me(accessToken: string, tokenType = 'Bearer') {
    return request<MeResponse>('/api/auth/me', {
      method: 'GET',
      token: accessToken,
      tokenType,
    });
  },
  logout(accessToken?: string | null, tokenType = 'Bearer') {
    return request<{ success: boolean; detail: string }>('/api/auth/logout', {
      method: 'POST',
      token: accessToken,
      tokenType,
    });
  },
};
