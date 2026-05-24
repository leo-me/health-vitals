import axios, { AxiosInstance } from "axios";
import { toApiError } from "./errors";

// CDL is unauthenticated — no bearer token, no on-401 handler needed.
// Baseline timeout shorter so the health badge fails fast when CDL is down.
function createClient(): AxiosInstance {
  const client = axios.create({
    baseURL: "/cdl",
    timeout: 10_000,
  });

  client.interceptors.response.use(
    (response) => response,
    (error) => Promise.reject(toApiError(error)),
  );

  return client;
}

export const cdlClient: AxiosInstance = createClient();
