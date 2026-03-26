import { Suspense } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';

import { AuthLayout } from '../auth/AuthLayout';
import { ProtectedRoute } from '../auth/ProtectedRoute';
import { AppShell } from '../layout/AppShell';
import { SettingsPage } from '../pages/SettingsPage';
import { DashboardPage } from '../pages/dashboard';
import { CreateLeadPage, EditLeadPage, LeadDetailPage, LeadsPage } from '../pages/leads';

export default function AppRoutes() {
	return (
		<Suspense
			fallback={
				<div className="flex min-h-screen items-center justify-center bg-background">
					<div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
				</div>
			}
		>
			<Routes>
				<Route path="/auth/*" element={<AuthLayout />} />
				<Route element={<ProtectedRoute />}>
					<Route element={<AppShell />}>
						<Route index element={<Navigate to="/dashboard" replace />} />
						<Route path="dashboard" element={<DashboardPage />} />
						<Route path="leads" element={<LeadsPage />} />
						<Route path="leads/new" element={<CreateLeadPage />} />
						<Route path="leads/:id" element={<LeadDetailPage />} />
						<Route path="leads/:id/edit" element={<EditLeadPage />} />
						<Route path="settings" element={<SettingsPage />} />
					</Route>
				</Route>
				<Route path="*" element={<Navigate to="/dashboard" replace />} />
			</Routes>
		</Suspense>
	);
}
