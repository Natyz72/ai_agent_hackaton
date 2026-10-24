import { CreateIncidentRequest, IncidentSummary, IncidentDetail } from '../types/api';
import { fetchApi } from './client';
import { mockCreateIncident, mockGetIncidents, mockGetIncident } from './mock';

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true';

export async function createIncident(request: CreateIncidentRequest): Promise<{ id: string; status: string }> {
  if (USE_MOCKS) {
    return mockCreateIncident(request);
  }
  return fetchApi<{ id: string; status: string }>('/api/incidents', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function getIncidents(): Promise<IncidentSummary[]> {
  if (USE_MOCKS) {
    return mockGetIncidents();
  }
  return fetchApi<IncidentSummary[]>('/api/incidents');
}

export async function getIncident(id: string): Promise<IncidentDetail> {
  if (USE_MOCKS) {
    return mockGetIncident(id);
  }
  return fetchApi<IncidentDetail>(`/api/incidents/${id}`);
}
