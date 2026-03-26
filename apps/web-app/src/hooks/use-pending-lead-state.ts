import { useCallback, useEffect, useMemo, useState } from 'react';

const STORAGE_KEY = 'aerolytic.web-app.pending-leads';
const EVENT_NAME = 'aerolytic:pending-leads';

export type PendingLeadMap = Record<string, number>;

function readPendingLeads(): PendingLeadMap {
  if (typeof window === 'undefined') {
    return {};
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return {};
  }

  try {
    return JSON.parse(raw) as PendingLeadMap;
  } catch {
    window.localStorage.removeItem(STORAGE_KEY);
    return {};
  }
}

function writePendingLeads(nextValue: PendingLeadMap) {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextValue));
  window.dispatchEvent(new CustomEvent(EVENT_NAME));
}

export function usePendingLeadState() {
  const [pendingLeads, setPendingLeads] = useState<PendingLeadMap>(() => readPendingLeads());

  useEffect(() => {
    const sync = () => setPendingLeads(readPendingLeads());

    window.addEventListener(EVENT_NAME, sync);
    window.addEventListener('storage', sync);

    return () => {
      window.removeEventListener(EVENT_NAME, sync);
      window.removeEventListener('storage', sync);
    };
  }, []);

  const markLeadPending = useCallback((leadId: string) => {
    const nextValue = {
      ...readPendingLeads(),
      [leadId]: Date.now(),
    };

    writePendingLeads(nextValue);
  }, []);

  const resolvePendingLead = useCallback((leadId: string) => {
    const nextValue = { ...readPendingLeads() };
    delete nextValue[leadId];
    writePendingLeads(nextValue);
  }, []);

  const pendingLeadIds = useMemo(() => new Set(Object.keys(pendingLeads)), [pendingLeads]);

  const getPendingSince = useCallback(
    (leadId: string) => pendingLeads[leadId] ?? null,
    [pendingLeads],
  );

  return {
    pendingLeadIds,
    getPendingSince,
    markLeadPending,
    resolvePendingLead,
  };
}
