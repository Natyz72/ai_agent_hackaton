import { ApiError } from '../types/api';

// HARD RULES: No secrets, API keys, or Supabase code in the frontend
export class ApiClientError extends Error {
  code: string;
  
  constructor(error: ApiError['error']) {
    super(error.message);
    this.name = 'ApiClientError';
    this.code = error.code;
  }
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(endpoint, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorData: ApiError;
    try {
      errorData = await response.json();
    } catch {
      errorData = {
        error: {
          code: 'UNKNOWN_ERROR',
          message: response.statusText || 'An unknown error occurred',
        },
      };
    }
    throw new ApiClientError(errorData.error);
  }

  return response.json();
}
