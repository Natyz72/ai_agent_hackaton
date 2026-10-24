import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { AppShell } from '../components/layout/AppShell';
import { getIncident } from '../api/incidents';
import { RiskBadge } from '../components/RiskBadge';
import { UncertaintyBanner } from '../components/UncertaintyBanner';
import { EvidenceHighlight } from '../components/EvidenceHighlight';
import { UrlList } from '../components/UrlList';
import { AttackSequence } from '../components/AttackSequence';
import { GuidanceCard } from '../components/GuidanceCard';
import { IndicatorCard } from '../components/IndicatorCard';
import { ActivityLog } from '../components/ActivityLog';
import { ErrorBanner } from '../components/ErrorBanner';
import { Spinner } from '../components/Spinner';
import { ArrowLeft } from 'lucide-react';
import { formatDate } from '../lib/format';

export function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const { data: incident, isLoading, isError, error } = useQuery({
    queryKey: ['incident', id],
    queryFn: () => getIncident(id!),
    enabled: !!id,
  });
  
  if (isLoading) {
    return (
      <AppShell showStepper={true}>
        <div className="flex items-center justify-center py-12">
          <Spinner className="w-8 h-8" />
        </div>
      </AppShell>
    );
  }
  
  if (isError || !incident) {
    return (
      <AppShell showStepper={true}>
        <div className="max-w-2xl mx-auto">
          <ErrorBanner
            message={error instanceof Error ? error.message : 'Incident not found'}
          />
          <button
            onClick={() => navigate('/incidents')}
            className="flex items-center gap-2 px-4 py-2 text-indigo-600 hover:text-indigo-700 min-h-[44px]"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to incidents
          </button>
        </div>
      </AppShell>
    );
  }
  
  const assessment = incident.assessment;
  const allEvidence = [
    ...assessment.indicators.flatMap(i => i.evidence),
    ...assessment.social_engineering.flatMap(i => i.evidence),
  ];
  
  return (
    <AppShell showStepper={true}>
      <div className="space-y-6">
        <div>
          <button
            onClick={() => navigate('/incidents')}
            className="flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-700 mb-4 min-h-[44px]"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to incidents
          </button>
          <h1 className="text-2xl font-semibold text-slate-900 mb-2">Incident {incident.id}</h1>
          <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600">
            <span>Created: {formatDate(incident.created_at)}</span>
            <span>Approved: {formatDate(incident.approved_at)}</span>
            <span>Status: {incident.status}</span>
            {incident.reviewed_by && <span>Reviewed by: {incident.reviewed_by}</span>}
            <span>Draft edited: {incident.draft_edited ? 'Yes' : 'No'}</span>
          </div>
        </div>
        
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <RiskBadge band={assessment.risk.band} />
                <span className="text-lg font-semibold text-slate-900">Risk Assessment</span>
              </div>
              <p className="text-sm text-slate-700 mb-3">{assessment.assessment}</p>
              <UncertaintyBanner />
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Original message</h2>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                <EvidenceHighlight text={assessment.message} evidences={allEvidence} />
              </div>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <UrlList urls={assessment.urls} />
            </div>
            
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Attack sequence</h2>
              <AttackSequence steps={assessment.attack_sequence} />
            </div>
            
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Retrieved guidance</h2>
              <div className="space-y-2">
                {assessment.guidance.map((guidance) => (
                  <GuidanceCard key={guidance.id} guidance={guidance} />
                ))}
              </div>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Final draft</h2>
              <pre className="text-sm text-slate-700 font-mono whitespace-pre-wrap bg-slate-50 p-3 rounded border border-slate-200">
                {incident.final_draft}
              </pre>
            </div>
          </div>
          
          {/* Right Column */}
          <div className="space-y-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Indicator checks</h2>
              
              {['credential_request', 'urgency', 'ip_address_link', 'trusted_domain_mismatch'].map((id) => {
                const indicator = assessment.indicators.find(i => i.id === id);
                if (indicator) {
                  return <IndicatorCard key={indicator.id} indicator={indicator} />;
                }
                return null;
              })}
              
              {assessment.indicators
                .filter(i => !['credential_request', 'urgency', 'ip_address_link', 'trusted_domain_mismatch'].includes(i.id))
                .map((indicator) => (
                  <IndicatorCard key={indicator.id} indicator={indicator} />
                ))}
              
              <h3 className="text-sm font-medium text-slate-900 mt-4 mb-2">Social engineering tactics</h3>
              {assessment.social_engineering.length === 0 ? (
                <p className="text-xs text-slate-600 italic">None detected</p>
              ) : (
                assessment.social_engineering.map((indicator) => (
                  <IndicatorCard key={indicator.id} indicator={indicator} />
                ))
              )}
              
              <h3 className="text-sm font-medium text-slate-900 mt-4 mb-2">Domain reputation</h3>
              <div className="space-y-2 mb-2">
                {assessment.domain_reputation.map((domain, index) => (
                  <div key={index} className="text-xs p-2 bg-slate-50 rounded border border-slate-200">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono text-slate-700">{domain.host}</span>
                      <span className={`px-1.5 py-0.5 rounded ${
                        domain.status === 'known_safe' ? 'bg-green-100 text-green-700' :
                        domain.status === 'known_suspicious' ? 'bg-red-100 text-red-700' :
                        'bg-slate-200 text-slate-700'
                      }`}>
                        {domain.status}
                      </span>
                    </div>
                    <div className="text-slate-600">Source: {domain.source}</div>
                    {domain.note && <div className="text-slate-600 mt-1">{domain.note}</div>}
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-500 italic">Unknown is not the same as safe or malicious.</p>
              
              <h3 className="text-sm font-medium text-slate-900 mt-4 mb-2">Risk breakdown</h3>
              <div className="space-y-1 mb-2">
                {assessment.risk.breakdown.map((item, index) => (
                  <div key={index} className="flex items-center justify-between text-xs">
                    <span className="text-slate-700">{item.rule}</span>
                    <span className="text-slate-900 font-medium">+{item.points}</span>
                  </div>
                ))}
                <div className="flex items-center justify-between text-xs font-medium pt-1 border-t border-slate-200">
                  <span className="text-slate-900">Total Score</span>
                  <span className="text-slate-900">{assessment.risk.score}</span>
                </div>
              </div>
              <p className="text-xs text-slate-500 italic">Heuristic score, not a probability.</p>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Next steps</h2>
              <ol className="list-decimal list-inside space-y-1">
                {assessment.next_steps.map((step, index) => (
                  <li key={index} className="text-sm text-slate-700">{step}</li>
                ))}
              </ol>
            </div>
            
            {assessment.activity && assessment.activity.length > 0 && (
              <ActivityLog activities={assessment.activity} />
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
