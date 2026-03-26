import { clearStoredTokens } from './storage';

function extractStatusCode(value: unknown): number | undefined {
  if (!value || typeof value !== 'object') {
    return undefined;
  }

  if ('statusCode' in value && typeof value.statusCode === 'number') {
    return value.statusCode;
  }

  if ('status' in value && typeof value.status === 'number') {
    return value.status;
  }

  if ('response' in value && value.response && typeof value.response === 'object') {
    const nestedStatus = extractStatusCode(value.response);
    if (nestedStatus) {
      return nestedStatus;
    }
  }

  if ('cause' in value && value.cause && typeof value.cause === 'object') {
    const nestedStatus = extractStatusCode(value.cause);
    if (nestedStatus) {
      return nestedStatus;
    }
  }

  if ('networkError' in value && value.networkError && typeof value.networkError === 'object') {
    const nestedStatus = extractStatusCode(value.networkError);
    if (nestedStatus) {
      return nestedStatus;
    }
  }

  return undefined;
}

function collectMessages(value: unknown): string[] {
  if (!value) {
    return [];
  }

  if (typeof value === 'string') {
    return [value];
  }

  if (Array.isArray(value)) {
    return value.flatMap(collectMessages);
  }

  if (typeof value !== 'object') {
    return [];
  }

  const messages: string[] = [];

  if ('message' in value && typeof value.message === 'string') {
    messages.push(value.message);
  }

  if ('errors' in value && Array.isArray(value.errors)) {
    messages.push(...value.errors.flatMap(collectMessages));
  }

  if ('cause' in value) {
    messages.push(...collectMessages(value.cause));
  }

  return messages;
}

export function isAuthFailureError(error: unknown) {
  const statusCode = extractStatusCode(error);
  if (statusCode === 401 || statusCode === 403) {
    return true;
  }

  return collectMessages(error).some((message) =>
    /(auth|unauthori[sz]ed|forbidden|csrf|permission denied|credentials were not provided)/i.test(message),
  );
}

export function logoutPortal() {
  clearStoredTokens();

  if (typeof window !== 'undefined' && window.location.pathname !== '/auth/login') {
    window.location.assign('/auth/login');
  }
}