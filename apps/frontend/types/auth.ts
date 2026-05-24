export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// JWT payload issued by apps/backend/app/core/security.py
export interface JwtClaims {
  sub: string; // user UUID
  exp: number; // seconds since epoch
  iat?: number;
}
