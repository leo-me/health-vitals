import axios, { AxiosInstance } from "axios";
import { toApiError } from "./errors";

// Late-wired by the admin layout on mount. Keeps this module free of any
// store import so we don't create a circular dependency.
let getToken: () => string | null = () => null;
let on401: () => void = () => {};

export function wireBackendAuth(deps: {
  getToken: () => string | null;
  on401: () => void;
}) {
  getToken = deps.getToken;
  on401 = deps.on401;
}

function createClient(): AxiosInstance {
  const client = axios.create({
    // Relative path — Next.js rewrites it to NEXT_PUBLIC_BACKEND_BASE_URL/api/v1/*.
    baseURL: "/backend",
  });

  client.interceptors.request.use((config) => {
    const token = getToken();
    if (token) {
      config.headers.set("Authorization", `Bearer ${token}`);
    }
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    (error) => {
      const apiError = toApiError(error);
      if (apiError.status === 401) {
        on401();
      }
      return Promise.reject(apiError);
    },
  );

  return client;
}

export const backendClient: AxiosInstance = createClient();
