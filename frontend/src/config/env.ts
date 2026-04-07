import { z } from 'zod';

const envSchema = z.object({
  BACKEND_URL: z.string().default(''),
  ENV: z.enum(['dev', 'prod']).default('dev'),
});

const parseEnv = () => {
  const rawEnv = {
    BACKEND_URL: import.meta.env.VITE_BACKEND_URL,
    ENV: import.meta.env.VITE_ENV,
  };

  const parsed = envSchema.safeParse(rawEnv);

  if (!parsed.success) {
    const issues = parsed.error.issues
      .map((issue) => `${issue.path.join('.')}: ${issue.message}`)
      .join('\n');
    throw new Error(
      `Invalid environment configuration. Check src/environments/.env.dev or .env.prod:\n${issues}`,
    );
  }

  return parsed.data;
};

export const env = parseEnv();
