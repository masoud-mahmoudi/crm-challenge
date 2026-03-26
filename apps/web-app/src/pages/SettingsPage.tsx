import { useMemo, useState } from 'react';
import { RefreshCw, ShieldCheck } from 'lucide-react';

import { useAuth } from '../auth/useAuth';
import { Alert, AlertDescription, AlertTitle } from '../components/alert';
import { Badge } from '../components/badge';
import { Button } from '../components/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/card';

export function SettingsPage() {
  const { logout, refreshProfile, session } = useAuth();
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const issuedAt = useMemo(() => {
    if (!session?.expiresAt) {
      return 'Unknown';
    }

    return new Date(session.expiresAt).toLocaleString();
  }, [session?.expiresAt]);

  if (!session) {
    return null;
  }

  const handleRefresh = async () => {
    setRefreshing(true);
    setError(null);
    setMessage(null);

    try {
      await refreshProfile();
      setMessage('User profile refreshed from the backend.');
    } catch (refreshError) {
      setError(refreshError instanceof Error ? refreshError.message : 'Unable to refresh profile.');
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_0.85fr]">
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-xl font-semibold">Account settings</CardTitle>
          <CardDescription>
            Inspect the active session and manually refresh the current user payload.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          {message ? (
            <Alert>
              <AlertTitle>Profile refreshed</AlertTitle>
              <AlertDescription>{message}</AlertDescription>
            </Alert>
          ) : null}
          {error ? (
            <Alert variant="destructive">
              <AlertTitle>Refresh failed</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : null}

          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Full name</p>
              <p className="mt-1 text-lg font-semibold">{session.user.full_name}</p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Email</p>
              <p className="mt-1 text-lg font-semibold">{session.user.email}</p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Session expiry</p>
              <p className="mt-1 text-sm font-medium">{issuedAt}</p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/35 p-4">
              <p className="text-sm text-muted-foreground">Membership count</p>
              <p className="mt-1 text-lg font-semibold">{session.memberships.length}</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <Button disabled={refreshing} onClick={handleRefresh} type="button">
              <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? 'Refreshing…' : 'Refresh /auth/me'}
            </Button>
            <Button onClick={() => void logout()} type="button" variant="outline">
              Sign out
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-xl font-semibold">
            <ShieldCheck className="h-5 w-5 text-primary" />
            Membership roles
          </CardTitle>
          <CardDescription>
            Active roles that came back from the backend for the current user.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3">
          {session.memberships.map((membership) => (
            <div key={membership.id} className="rounded-2xl border border-border bg-card p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="font-medium">{membership.company.name}</p>
                  <p className="text-sm text-muted-foreground">{membership.company.company_type}</p>
                </div>
                <Badge variant={membership.is_active ? 'secondary' : 'destructive'}>
                  {membership.role}
                </Badge>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
