import type {
  EnrichmentStatus,
  GraphqlActivity,
  GraphqlCompany,
  GraphqlLead,
  GraphqlMe,
  LeadViewModel,
} from '../types/crm';

const EMAIL_PATTERN = /^Email:\s*(.+)$/im;
const PHONE_PATTERN = /^Phone:\s*(.+)$/im;

function extractMetadata(pattern: RegExp, value?: string | null) {
  if (!value) {
    return null;
  }

  const match = pattern.exec(value);
  return match?.[1]?.trim() || null;
}

export function resolveOwnerName(me: GraphqlMe, ownerUserId?: string | null) {
  if (!ownerUserId) {
    return 'Unassigned';
  }

  if (!me?.user) {
    return ownerUserId;
  }

  return me.user.id === ownerUserId ? me.user.fullName || me.user.email : ownerUserId;
}

export function resolveCompanyName(companies: GraphqlCompany[], companyId?: string | null) {
  if (!companyId) {
    return 'Unassigned';
  }

  return (companies ?? []).find((company) => company.id === companyId)?.name ?? companyId;
}

export function resolveEnrichmentStatus(options: {
  activities: GraphqlActivity[];
  pendingSince: number | null;
}): EnrichmentStatus {
  if (options.activities.length > 0) {
    return 'COMPLETED';
  }

  if (options.pendingSince && Date.now() - options.pendingSince < 45_000) {
    return 'PENDING';
  }

  return 'PROCESSING';
}

export function buildLeadViewModel(options: {
  lead: GraphqlLead;
  me: GraphqlMe;
  companies?: GraphqlCompany[];
  activities?: GraphqlActivity[];
  pendingSince?: number | null;
}): LeadViewModel {
  const { lead, me, companies = [], activities = [], pendingSince = null } = options;
  const derivedEnrichmentStatus = resolveEnrichmentStatus({ activities, pendingSince });

  return {
    id: lead.id,
    name: lead.name || lead.title,
    email: lead.email ?? extractMetadata(EMAIL_PATTERN, lead.description),
    phone: lead.phone ?? extractMetadata(PHONE_PATTERN, lead.description),
    status: lead.status || 'NEW',
    enrichmentStatus:
      activities.length > 0
        ? 'COMPLETED'
        : ((lead.enrichmentStatus as EnrichmentStatus | null | undefined) ?? derivedEnrichmentStatus),
    score: lead.score ?? null,
    companyId: lead.companyId ?? null,
    companyName: resolveCompanyName(companies, lead.companyId),
    ownerUserId: lead.ownerUserId ?? null,
    ownerName: resolveOwnerName(me, lead.ownerUserId),
    source: lead.source ?? null,
    description: lead.description ?? null,
    createdAt: lead.createdAt ?? null,
    updatedAt: lead.updatedAt ?? null,
  };
}
