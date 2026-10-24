import { InvestigateRequest, InvestigateResponse } from '../types/api';
import { fetchApi } from './client';
import { mockInvestigate } from './mock';

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true';

export async function investigateMessage(request: InvestigateRequest): Promise<InvestigateResponse> {
  if (USE_MOCKS) {
    return mockInvestigate(request);
  }
  return fetchApi<InvestigateResponse>('/api/investigate', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}
