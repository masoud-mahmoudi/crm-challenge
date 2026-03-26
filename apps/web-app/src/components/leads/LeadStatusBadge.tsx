import { Badge } from '../badge';

interface LeadStatusBadgeProps {
  status: string;
}

const toneMap: Record<string, string> = {
  new: 'bg-sky-100 text-sky-800 border-sky-200',
  open: 'bg-sky-100 text-sky-800 border-sky-200',
  qualified: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  won: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  closed: 'bg-slate-100 text-slate-700 border-slate-200',
  lost: 'bg-rose-100 text-rose-700 border-rose-200',
};

export function LeadStatusBadge({ status }: LeadStatusBadgeProps) {
  const key = status.toLowerCase();

  return (
    <Badge variant="secondary" className={`border ${toneMap[key] ?? 'bg-amber-100 text-amber-800 border-amber-200'}`}>
      {status}
    </Badge>
  );
}
