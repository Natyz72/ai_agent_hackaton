import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { AppShell } from '../components/layout/AppShell';
import { getIncidents } from '../api/incidents';
import { RiskBadge } from '../components/RiskBadge';
import { EmptyState } from '../components/EmptyState';
import { ErrorBanner } from '../components/ErrorBanner';
import { Skeleton } from '../components/Spinner';
import { formatDate } from '../lib/format';
import { ChevronRight } from 'lucide-react';

export function IncidentsPage() {
  const navigate = useNavigate();
  
  const { data: incidents, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['incidents'],
    queryFn: getIncidents,
  });
  
  return (
    <AppShell showStepper={true}>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 mb-2">Saved Incidents</h1>
          <p className="text-sm text-slate-600">History of reviewed and saved investigations</p>
        </div>
        
        {isError && (
          <ErrorBanner
            message={error instanceof Error ? error.message : 'Failed to load incidents'}
            onRetry={() => refetch()}
          />
        )}
        
        {isLoading && (
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="p-4 space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-4">
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-6 w-24" />
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 w-20" />
                </div>
              ))}
            </div>
          </div>
        )}
        
        {!isLoading && !isError && incidents && incidents.length === 0 && (
          <EmptyState message="No incidents saved yet." />
        )}
        
        {!isLoading && !isError && incidents && incidents.length > 0 && (
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th scope="col" className="text-left text-xs font-medium text-slate-600 px-4 py-3">
                      ID
                    </th>
                    <th scope="col" className="text-left text-xs font-medium text-slate-600 px-4 py-3">
                      Date
                    </th>
                    <th scope="col" className="text-left text-xs font-medium text-slate-600 px-4 py-3">
                      Risk
                    </th>
                    <th scope="col" className="text-left text-xs font-medium text-slate-600 px-4 py-3">
                      Status
                    </th>
                    <th scope="col" className="text-left text-xs font-medium text-slate-600 px-4 py-3">
                      Reviewer
                    </th>
                    <th scope="col" className="text-right text-xs font-medium text-slate-600 px-4 py-3">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {incidents.map((incident) => (
                    <tr
                      key={incident.id}
                      className="hover:bg-slate-50 cursor-pointer transition-colors"
                      onClick={() => navigate(`/incidents/${incident.id}`)}
                    >
                      <td className="px-4 py-3 text-sm font-mono text-slate-900">
                        {incident.id}
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-700">
                        {formatDate(incident.created_at)}
                      </td>
                      <td className="px-4 py-3">
                        <RiskBadge band={incident.risk_band} />
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-700">
                        {incident.status}
                      </td>
                      <td className="px-4 py-3 text-sm text-slte-700">
                        {incident.reviewed_by || '-'}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          className="inline-flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-700 min-h-[44px]"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/incidents/${incident.id}`);
                          }}
                          aria-label={`Open ${incident.id}`}
                        >
                          Open
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
