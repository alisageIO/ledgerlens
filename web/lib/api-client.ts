import { env } from "./env";

interface Envelope<T> {
  success: boolean;
  statusCode: number;
  message: string;
  data: T | null;
  meta: Record<string, unknown> | null;
}

export class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Calls the FastAPI backend and unwraps the standard envelope (TRD §5). */
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${env.NEXT_PUBLIC_API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  const envelope = (await response.json()) as Envelope<T>;
  if (!envelope.success || envelope.data === null) {
    throw new ApiError(envelope.statusCode, envelope.message);
  }
  return envelope.data;
}
