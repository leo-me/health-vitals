import { jwtDecode } from "jwt-decode";
import type { JwtClaims } from "@/types/auth";

export function decodeToken(token: string): JwtClaims {
  return jwtDecode<JwtClaims>(token);
}

/** True if the JWT exp claim (seconds-since-epoch) is in the past. */
export function isExpired(exp: number, nowMs: number = Date.now()): boolean {
  return exp * 1000 <= nowMs;
}
