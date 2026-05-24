// Type mirrors for the FastAPI backend (apps/backend/app/schemas/*).

export type SensorType =
  | "heart_rate"
  | "eda"
  | "bvp"
  | "acc"
  | "ibi"
  | "temp"
  | "accelerometer";

export const SENSOR_TYPES: SensorType[] = [
  "heart_rate",
  "eda",
  "bvp",
  "acc",
  "ibi",
  "temp",
  "accelerometer",
];

export type DeviceType = "phone" | "sensor" | "watch";
export const DEVICE_TYPES: DeviceType[] = ["phone", "sensor", "watch"];

export type UserType = "patient" | "caregiver" | "admin";

export interface UserResponse {
  id: string;
  email: string;
  name?: string | null;
  sex?: "male" | "female" | "intersex" | null;
  age?: number | null;
  weight?: number | null;
  illness_history?: string | null;
  user_type?: UserType | null;
  caregiver_id?: string | null;
  created_at: string;
}

export interface DeviceResponse {
  id: string;
  user_id: string | null;
  type: DeviceType;
  created_at: string;
  serial_number: string | null;
}

export interface DeviceCreate {
  user_id?: string;
  type: DeviceType;
  push_token?: string;
  serial_number?: string;
}

export type DeviceUpdate = Partial<DeviceCreate>;

export interface SensorRecordingResponse {
  id: string;
  device_id: string;
  user_id: string;
  timestamp: string;
  sensor_type: SensorType;
  data: Record<string, unknown>;
  created_at: string;
}

export interface SensorRecordingsQuery {
  sensor_type?: SensorType;
  start?: string;
  end?: string;
  page?: number;
  page_size?: number;
}

export interface AlertResponse {
  id: string;
  user_id: string;
  content: string;
  created_at: string;
}
