import { FormEvent, useMemo, useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { LockKeyhole, LogIn, UserCircle2 } from 'lucide-react';

import { Alert, AlertDescription, AlertTitle } from '../components/alert';
import { Button } from '../components/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/card';
import { Input } from '../components/input';
import { useAuth } from './useAuth';

type LocationState = {
  from?: {
    pathname?: string;
  };
};

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, login, loading } = useAuth();

  const [email, setEmail] = useState('ops-admin@aerialytic.io');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const targetPath = useMemo(() => {
    const state = location.state as LocationState | null;
    return state?.from?.pathname && state.from.pathname !== '/auth/login' ? state.from.pathname : '/';
  }, [location.state]);

  if (isAuthenticated && !loading) {
    return <Navigate to={targetPath} replace />;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await login({ email, password });
      navigate(targetPath, { replace: true });
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Unable to sign in.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background px-4 py-10">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(0,105,112,0.12),transparent_30%),radial-gradient(circle_at_bottom_right,rgba(0,44,163,0.10),transparent_28%)]" />
      <div className="relative grid w-full max-w-6xl gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-[28px] border border-border bg-card/85 p-8 shadow-xl backdrop-blur md:p-10">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary">Aerialytic</p>
          <h1 className="mt-4 max-w-xl text-4xl font-semibold tracking-tight text-foreground md:text-5xl">
            Sign in to the control plane.
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-muted-foreground md:text-lg">
            Authenticate against the API gateway, fetch your current user profile from the backend,
            and load workspace companies and memberships into the dashboard.
          </p>
          <div className="mt-8 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-border bg-muted/60 p-5">
              <div className="mb-3 inline-flex rounded-full bg-primary/10 p-3 text-primary">
                <LockKeyhole className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-semibold">JWT-based sign-in</h2>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                Uses the backend login endpoint, stores the issued token pair, and restores the
                session from local storage.
              </p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/60 p-5">
              <div className="mb-3 inline-flex rounded-full bg-primary/10 p-3 text-primary">
                <UserCircle2 className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-semibold">Live /auth/me data</h2>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                Hydrates the app shell with the current user, memberships, and accessible companies
                returned by the gateway.
              </p>
            </div>
          </div>
        </div>

        <Card className="border-border/80 bg-card/95 shadow-xl backdrop-blur">
          <CardHeader>
            <CardTitle className="text-2xl font-semibold tracking-tight">Welcome back</CardTitle>
            <CardDescription>
              Use a seeded backend account or replace the credentials with your own.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form className="grid gap-4" onSubmit={handleSubmit}>
              {error ? (
                <Alert variant="destructive">
                  <AlertTitle>Sign-in failed</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              ) : null}

              <label className="grid gap-2 text-sm font-medium">
                Email
                <Input
                  autoComplete="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="name@company.com"
                  type="email"
                  required
                />
              </label>

              <label className="grid gap-2 text-sm font-medium">
                Password
                <Input
                  autoComplete="current-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="••••••••"
                  type="password"
                  required
                />
              </label>

              <Button className="mt-2 w-full" disabled={submitting} type="submit">
                <LogIn className="mr-2 h-4 w-4" />
                {submitting ? 'Signing in…' : 'Sign in'}
              </Button>

              <div className="rounded-2xl border border-dashed border-border bg-muted/45 p-4 text-sm text-muted-foreground">
                <p className="font-medium text-foreground">Local development defaults</p>
                <p className="mt-1">Email: parent.admin@aerialytic.com</p>
                <p>Password: password123</p>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
