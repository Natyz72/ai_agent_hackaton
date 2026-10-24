import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { useInvestigation } from '../state/InvestigationContext';
import { RiskBadge } from '../components/RiskBadge';
import { UncertaintyBanner } from '../components/UncertaintyBanner';
import { EvidenceHighlight } from '../components/EvidenceHighlight';
import { UrlList } from '../components/UrlList';
import { AttackSequence } from '../components/AttackSequence';
import { GuidanceCard } from '../components/GuidanceCard';
import { IndicatorCard } from '../components/IndicatorCard';
import { ActivityLog } from '../components/ActivityLog';
import { Edit, ArrowRight } from 'lucide-react';

export function ResultsPage() {
  const navigate = useNavigate();
  const { getAssessment } = useInvestigation();
  const assessment = getAssessment();
  
  if (!assessment) {
    navigate('/');
    return null;
  }
  
  // Collect all evidence from indicators and social engineering
  const allEvidence = [
    ...assessment.indicators.flatMap(i => i.evidence),
    ...assessment.social_engineering.flatMap(i => i.evidence),
  ];
  
  return (
    <AppShell showStepper={true}>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 mb-4">Analysis Results</h1>
          
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm mb-4">
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
          </div>
          
          {/* Right Column */}
          <div className="space-y-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Indicator checks</h2>
              <p className="text-xs text-slate-600 mb-3">
                Required indicators in order: Credential request, Urgency, IP-address link, Trusted-domain mismatch
              </p>
              
              {/* 4 required first */}
              {['credential_request', 'urgency', 'ip_address_link', 'trusted_domain_mismatch'].map((id) => {
                const indicator = assessment.indicators.find(i => i.id === id);
                if (indicator) {
                  return <IndicatorCard key={indicator.id} indicator={indicator} />;
                }
                return null;
              })}
              
              {/* Additional indicators */}
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
            
            {!assessment.validation.passed && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                <p className="text-sm font-medium text-amber-900 mb-2">Validation Issues</p>
                <ul className="space-y-1">
                  {assessment.validation.issues.map((issue, index) => (
                    <li key={index} className="text-xs text-amber-800">• {issue}</li>
                  ))}
                </ul>
              </div>
            )}
            
            <ActivityLog activities={assessment.activity} />
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3 pt-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center justify-center gap-2 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors min-h-[44px]"
          >
            <Edit className="w-4 h-4" />
            Edit message
          </button>
          <button
            onClick={() => navigate('/review')}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium min-h-[44px] flex-1 sm:flex-initial"
          >
            Continue to Review
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </AppShell>
  );
}
