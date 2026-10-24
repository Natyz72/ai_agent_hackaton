import { ApiError } from '../types/api';

// HARD RULES: No secrets, API keys, or Supabase code in the frontend
export class ApiClientError extends Error {
  code: string;

  constructor(error: ApiError['error']) {
    super(error?.message || 'An unknown error occurred');
    this.name = 'ApiClientError';
    this.code = error?.code || 'UNKNOWN_ERROR';
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
    let code = `HTTP_${response.status}`;
    let message = response.statusText || 'An unknown error occurred';

    try {
      const data = await response.json();
      if (data?.error?.message) {
        message = data.error.message;
        code = data.error.code || code;
      } else if (typeof data?.detail === 'string') {
        message = data.detail;
      } else if (Array.isArray(data?.detail) && data.detail.length > 0) {
        message = data.detail[0]?.msg || JSON.stringify(data.detail);
      } else if (data?.message) {
        message = data.message;
      }
    } catch {
      // Non-JSON response body
    }

    throw new ApiClientError({ code, message });
  }

  return response.json();
}
