import { useEffect, useMemo, useState, type FormEvent } from 'react';

import type { GraphqlCompany, LeadFormValues, UpdateLeadInput } from '../../types/crm';
import { Alert, AlertDescription, AlertTitle } from '../alert';
import { Button } from '../button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../card';
import { Input } from '../input';

export interface LeadFormOwnerOption {
  id: string;
  label: string;
}

interface LeadFormProps {
  companies: GraphqlCompany[];
  owners: LeadFormOwnerOption[];
  mode?: 'create' | 'edit';
  initialValues?: Partial<UpdateLeadInput>;
  submitting?: boolean;
  submitError?: string | null;
  onSubmit: (values: LeadFormValues) => Promise<void>;
}

const STATUS_OPTIONS = ['NEW', 'CONTACTED', 'QUALIFIED', 'LOST'];

export function LeadForm({
  companies,
  owners,
  mode = 'create',
  initialValues,
  submitting = false,
  submitError,
  onSubmit,
}: LeadFormProps) {
  const [companyId, setCompanyId] = useState(initialValues?.companyId ?? companies[0]?.id ?? '');
  const [name, setName] = useState(initialValues?.name ?? '');
  const [email, setEmail] = useState(initialValues?.email ?? '');
  const [phone, setPhone] = useState(initialValues?.phone ?? '');
  const [source, setSource] = useState(initialValues?.source ?? 'web-app');
  const [status, setStatus] = useState(initialValues?.status ?? 'NEW');
  const [ownerUserId, setOwnerUserId] = useState(initialValues?.ownerUserId ?? '');
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    setCompanyId(initialValues?.companyId ?? companies[0]?.id ?? '');
    setName(initialValues?.name ?? '');
    setEmail(initialValues?.email ?? '');
    setPhone(initialValues?.phone ?? '');
    setSource(initialValues?.source ?? 'web-app');
    setStatus(initialValues?.status ?? 'NEW');
    setOwnerUserId(initialValues?.ownerUserId ?? '');
  }, [companies, initialValues]);

  const canSubmit = useMemo(
    () => (mode === 'edit' || companyId.trim().length > 0) && name.trim().length > 0 && email.trim().length > 0,
    [companyId, email, mode, name],
  );

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!canSubmit) {
      setValidationError(mode === 'edit' ? 'Lead name and email are required.' : 'Company, lead name, and email are required.');
      return;
    }

    setValidationError(null);

    await onSubmit({
      companyId,
      name,
      email,
      phone: phone || undefined,
      ownerUserId: ownerUserId || undefined,
      source: source || undefined,
      status,
    });
  };

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="text-2xl font-semibold tracking-tight">{mode === 'edit' ? 'Update lead' : 'Create lead'}</CardTitle>
        <CardDescription>
          {mode === 'edit'
            ? 'The form writes to GraphQL `updateLead` and keeps the current lead detail page in sync.'
            : 'The form writes to GraphQL `createLead` so new leads appear in the pipeline immediately.'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form className="grid gap-5" onSubmit={handleSubmit}>
          {validationError ? (
            <Alert variant="destructive">
              <AlertTitle>Missing required fields</AlertTitle>
              <AlertDescription>{validationError}</AlertDescription>
            </Alert>
          ) : null}
          {submitError ? (
            <Alert variant="destructive">
              <AlertTitle>{mode === 'edit' ? 'Could not update lead' : 'Could not create lead'}</AlertTitle>
              <AlertDescription>{submitError}</AlertDescription>
            </Alert>
          ) : null}

          {mode === 'create' ? (
            <label className="grid gap-2 text-sm font-medium">
              Company
              <select
                className="border-input bg-input-background focus-visible:border-ring focus-visible:ring-ring/50 flex h-10 w-full rounded-md border px-3 py-2 outline-none focus-visible:ring-[3px]"
                onChange={(event) => setCompanyId(event.target.value)}
                value={companyId}
              >
                {companies.map((company) => (
                  <option key={company.id} value={company.id}>
                    {company.name}
                  </option>
                ))}
              </select>
            </label>
          ) : null}

          <div className="grid gap-5 md:grid-cols-2">
            <label className="grid gap-2 text-sm font-medium">
              Name
              <Input
                onChange={(event) => setName(event.target.value)}
                placeholder="Jane Doe"
                value={name}
              />
            </label>
            <label className="grid gap-2 text-sm font-medium">
              Email
              <Input
                onChange={(event) => setEmail(event.target.value)}
                placeholder="jane@company.com"
                type="email"
                value={email}
              />
            </label>
            <label className="grid gap-2 text-sm font-medium">
              Phone
              <Input
                onChange={(event) => setPhone(event.target.value)}
                placeholder="+1 555 010 1234"
                value={phone}
              />
            </label>
            <label className="grid gap-2 text-sm font-medium">
              Source
              <Input
                onChange={(event) => setSource(event.target.value)}
                placeholder="web-app"
                value={source}
              />
            </label>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            {mode === 'create' ? (
              <label className="grid gap-2 text-sm font-medium">
                Assign owner (optional)
                <select
                  className="border-input bg-input-background focus-visible:border-ring focus-visible:ring-ring/50 flex h-10 w-full rounded-md border px-3 py-2 outline-none focus-visible:ring-[3px]"
                  onChange={(event) => setOwnerUserId(event.target.value)}
                  value={ownerUserId}
                >
                  <option value="">Leave unassigned</option>
                  {owners.map((owner) => (
                    <option key={owner.id} value={owner.id}>
                      {owner.label}
                    </option>
                  ))}
                </select>
              </label>
            ) : null}

            <label className="grid gap-2 text-sm font-medium">
              Status
              <select
                className="border-input bg-input-background focus-visible:border-ring focus-visible:ring-ring/50 flex h-10 w-full rounded-md border px-3 py-2 outline-none focus-visible:ring-[3px]"
                onChange={(event) => setStatus(event.target.value)}
                value={status}
              >
                {STATUS_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button disabled={submitting || !canSubmit} type="submit">
              {submitting ? (mode === 'edit' ? 'Saving changes…' : 'Creating lead…') : mode === 'edit' ? 'Save changes' : 'Create lead'}
            </Button>
            <p className="text-sm text-muted-foreground">
              {mode === 'edit'
                ? 'Lead removal is not available yet because the current GraphQL schema does not expose a delete mutation.'
                : 'New leads enter the workflow in a pending enrichment state.'}
            </p>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
