// Type mirrors for the Consumer Delivery Layer (apps/consumer_delivery/schemas/*).

export type ConsumerType = "smart_watch" | "web_dashboard" | "ml" | "researcher";
export const CONSUMER_TYPES: ConsumerType[] = [
  "smart_watch",
  "web_dashboard",
  "ml",
  "researcher",
];

export type CdlSensorType = "heart_rate" | "eda" | "bvp" | "acc" | "temp";

export interface OverviewBucket {
  bucket: string; // ISO8601 hourly bucket
  sensor_type: CdlSensorType;
  n: number;
  avg: number | null;
  max: number | null;
  min: number | null;
}

export interface OverviewResponse {
  user_id: string;
  days: number;
  bucket_count: number;
  cache_hit: boolean;
  db_ms?: number; // only present on cache miss
  buckets: OverviewBucket[];
}

export type StressLabel = "stress" | "non_stress";

export interface InferenceResponse {
  user_id: string;
  timestamp: string;
  prediction: 0 | 1;
  label: StressLabel;
  probabilities: number[] | null;
  model: {
    registry_id: string;
    run_id: string;
    model_name: string;
    algorithm: string | null;
    feature_version: "v1" | "v2";
    metrics: Record<string, unknown>;
  };
}

// Adapter responses vary in shape per consumer; keep as unknown record.
export type AdapterResponse = Record<string, unknown>;

export interface PingResponse {
  response: "pong";
}
