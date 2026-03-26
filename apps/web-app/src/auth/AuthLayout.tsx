import { Navigate, Route, Routes } from 'react-router-dom';

import { useAuth } from './useAuth';
import { LoginPage } from './LoginPage';

export function AuthLayout() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route
        index
        element={<Navigate to={isAuthenticated ? '/' : '/auth/login'} replace />}
      />
      <Route
        path="login"
        element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />}
      />
      <Route path="*" element={<Navigate to="/auth/login" replace />} />
    </Routes>
  );
}
