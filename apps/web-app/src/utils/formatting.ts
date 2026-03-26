export function formatDateTime(value?: string | null) {
  if (!value) {
    return '—';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

export function formatCompactDate(value?: string | null) {
  if (!value) {
    return '—';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
  }).format(date);
}

export function formatNullable(value?: string | null) {
  if (!value || value.trim().length === 0) {
    return '—';
  }

  return value;
}

export function formatRelativeMinutes(timestamp: number) {
  const minutes = Math.max(0, Math.round((Date.now() - timestamp) / 60000));

  if (minutes === 0) {
    return 'just now';
  }

  if (minutes === 1) {
    return '1 minute ago';
  }

  return `${minutes} minutes ago`;
}
