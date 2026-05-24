import { backendClient } from "./backend";
import { cdlClient } from "./cdl";
import type {
  AlertResponse,
  DeviceCreate,
  DeviceResponse,
  DeviceUpdate,
  SensorRecordingResponse,
  SensorRecordingsQuery,
  UserResponse,
} from "@/types/backend";
import type {
  AdapterResponse,
  ConsumerType,
  InferenceResponse,
  OverviewResponse,
  PingResponse,
} from "@/types/cdl";
import type { TokenResponse } from "@/types/auth";

// ---------- Auth ----------

/**
 * POST /api/v1/auth/login — form-urlencoded (NOT JSON). Backend uses
 * OAuth2PasswordRequestForm so the body must be x-www-form-urlencoded.
 */
export async function loginRequest(
  email: string,
  password: string,
  signal?: AbortSignal,
): Promise<TokenResponse> {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);
  const res = await backendClient.post<TokenResponse>("/auth/login", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    signal,
  });
  return res.data;
}

// ---------- Users ----------

export async function getUser(userId: string, signal?: AbortSignal): Promise<UserResponse> {
  const res = await backendClient.get<UserResponse>(`/users/${userId}`, { signal });
  return res.data;
}

// ---------- Devices ----------

export async function listDevices(userId: string, signal?: AbortSignal): Promise<DeviceResponse[]> {
  const res = await backendClient.get<DeviceResponse[]>(`/device/user/${userId}`, { signal });
  return res.data;
}

export async function createDevice(body: DeviceCreate): Promise<DeviceResponse> {
  const res = await backendClient.post<DeviceResponse>("/device/", body);
  return res.data;
}

export async function updateDevice(
  deviceId: string,
  body: DeviceUpdate,
): Promise<DeviceResponse> {
  const res = await backendClient.patch<DeviceResponse>(`/device/${deviceId}`, body);
  return res.data;
}

export async function deleteDevice(deviceId: string): Promise<void> {
  await backendClient.delete(`/device/${deviceId}`);
}

// ---------- Sensor recordings ----------

export async function listSensorRecordings(
  userId: string,
  query: SensorRecordingsQuery = {},
  signal?: AbortSignal,
): Promise<SensorRecordingResponse[]> {
  const res = await backendClient.get<SensorRecordingResponse[]>(
    `/sensor_recordings/user/${userId}`,
    { params: query, signal },
  );
  return res.data;
}

// ---------- Alerts ----------

export async function listAlerts(userId: string, signal?: AbortSignal): Promise<AlertResponse[]> {
  const res = await backendClient.get<AlertResponse[]>(`/alert/user/${userId}`, { signal });
  return res.data;
}

// ---------- CDL ----------

export async function getOverview(
  userId: string,
  days: number = 7,
  signal?: AbortSignal,
): Promise<OverviewResponse> {
  const res = await cdlClient.get<OverviewResponse>(`/overview/${userId}`, {
    params: { days },
    signal,
  });
  return res.data;
}

export async function getInference(
  userId: string,
  signal?: AbortSignal,
): Promise<InferenceResponse> {
  const res = await cdlClient.get<InferenceResponse>(`/inference/${userId}`, { signal });
  return res.data;
}

export async function getAdapterData(
  consumerType: ConsumerType,
  userId: string,
  signal?: AbortSignal,
): Promise<AdapterResponse> {
  const res = await cdlClient.get<AdapterResponse>(`/data/${consumerType}/${userId}`, { signal });
  return res.data;
}

export async function pingCdl(signal?: AbortSignal): Promise<PingResponse> {
  const res = await cdlClient.get<PingResponse>("/ping", { signal });
  return res.data;
}
