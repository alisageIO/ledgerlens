import { z } from "zod";

const envSchema = z.object({
  NEXT_PUBLIC_API_URL: z.url(),
});

/**
 * Validated at import time so a missing/malformed env var fails fast at
 * build/boot rather than surfacing as an obscure runtime fetch error deep in
 * a component — no module outside this file should read `process.env`
 * directly (mirrors the backend's config/env.py convention).
 */
export const env = envSchema.parse({
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
});
