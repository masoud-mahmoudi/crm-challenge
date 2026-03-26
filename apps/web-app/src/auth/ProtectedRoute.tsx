import { Navigate, Outlet, useLocation } from 'react-router-dom';

import { Card, CardContent } from '../components/card';
import { useAuth } from './useAuth';

export function ProtectedRoute() {
  const location = useLocation();
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background px-4">
        <Card className="w-full max-w-md shadow-sm">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            <div>
              <p className="font-medium">Restoring your session</p>
              <p className="text-sm text-muted-foreground">Checking saved tokens and loading your workspace.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
