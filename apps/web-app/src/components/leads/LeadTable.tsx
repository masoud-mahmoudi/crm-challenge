import { useNavigate } from 'react-router-dom';

import type { LeadViewModel } from '../../types/crm';
import { formatCompactDate, formatNullable } from '../../utils/formatting';
import { Card, CardContent, CardHeader, CardTitle } from '../card';
import { EnrichmentStatusBadge } from './EnrichmentStatusBadge';
import { LeadStatusBadge } from './LeadStatusBadge';

interface LeadTableProps {
  leads: LeadViewModel[];
  isRefreshing?: boolean;
}

export function LeadTable({ leads, isRefreshing = false }: LeadTableProps) {
  const navigate = useNavigate();

  return (
    <Card className="shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xl font-semibold">Lead pipeline</CardTitle>
        {isRefreshing ? <span className="text-sm text-muted-foreground">Refreshing…</span> : null}
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="min-w-full border-separate border-spacing-y-3">
            <thead>
              <tr className="text-left text-sm text-muted-foreground">
                <th className="px-3 py-2 font-medium">Lead</th>
                <th className="px-3 py-2 font-medium">Company</th>
                <th className="px-3 py-2 font-medium">Owner</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium">Enrichment</th>
                <th className="px-3 py-2 font-medium">Score</th>
                <th className="px-3 py-2 font-medium">Updated</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr
                  key={lead.id}
                  aria-label={`Open ${lead.name}`}
                  className="cursor-pointer rounded-2xl border border-border bg-card shadow-sm transition-colors hover:bg-muted/35 focus:outline-none focus:ring-2 focus:ring-ring"
                  onClick={() => navigate(`/leads/${lead.id}`)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault();
                      navigate(`/leads/${lead.id}`);
                    }
                  }}
                  tabIndex={0}
                >
                  <td className="rounded-l-2xl px-3 py-3 align-top">
                    <span className="font-medium text-primary">{lead.name}</span>
                    <div className="mt-1 text-sm text-muted-foreground">{formatNullable(lead.email)}</div>
                  </td>
                  <td className="px-3 py-3 align-top text-sm">{formatNullable(lead.companyName)}</td>
                  <td className="px-3 py-3 align-top text-sm">{formatNullable(lead.ownerName)}</td>
                  <td className="px-3 py-3 align-top text-sm">
                    <LeadStatusBadge status={lead.status} />
                  </td>
                  <td className="px-3 py-3 align-top text-sm">
                    <EnrichmentStatusBadge status={lead.enrichmentStatus} />
                  </td>
                  <td className="px-3 py-3 align-top text-sm">{lead.score ?? '—'}</td>
                  <td className="rounded-r-2xl px-3 py-3 align-top text-sm text-muted-foreground">
                    {formatCompactDate(lead.updatedAt ?? lead.createdAt)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
