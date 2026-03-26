import type { EnrichmentStatus } from '../../types/crm';
import { Badge } from '../badge';

interface EnrichmentStatusBadgeProps {
  status: EnrichmentStatus;
}

const toneMap: Record<EnrichmentStatus, string> = {
  PENDING: 'bg-amber-100 text-amber-800 border-amber-200',
  PROCESSING: 'bg-sky-100 text-sky-800 border-sky-200',
  COMPLETED: 'bg-emerald-100 text-emerald-800 border-emerald-200',
};

const labelMap: Record<EnrichmentStatus, string> = {
  PENDING: 'Pending enrichment',
  PROCESSING: 'Processing',
  COMPLETED: 'Completed',
};

export function EnrichmentStatusBadge({ status }: EnrichmentStatusBadgeProps) {
  return (
    <Badge variant="secondary" className={`border ${toneMap[status]}`}>
      {labelMap[status]}
    </Badge>
  );
}
