export interface CompanySummary {
  id: string;
  name: string;
  company_type: string;
  parent_id: string | null;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Membership {
  id: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  company: CompanySummary;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_staff: boolean;
  created_at: string;
  memberships?: Membership[];
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
  user?: UserProfile;
}

export interface MeResponse {
  user: UserProfile;
  memberships: Membership[];
  accessible_companies: CompanySummary[];
}

export interface AuthTokens {
  accessToken: string | null;
  refreshToken: string | null;
  tokenType: string;
  expiresAt: number | null;
}

export interface AuthSession extends AuthTokens, MeResponse {}
