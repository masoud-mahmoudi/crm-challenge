import { BrowserRouter } from 'react-router-dom';

import { AuthProvider } from './auth/auth-context';
import { AppProviders } from './providers/AppProviders';
import Router from './route/router';

export default function App() {
  return (
    <AuthProvider>
      <AppProviders>
        <BrowserRouter>
          <Router />
        </BrowserRouter>
      </AppProviders>
    </AuthProvider>
  );
}