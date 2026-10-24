import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { AppShell } from '../components/layout/AppShell';
import { useInvestigation } from '../state/InvestigationContext';
import { createIncident } from '../api/incidents';
import { RiskBadge } from '../components/RiskBadge';
import { UncertaintyBanner } from '../components/UncertaintyBanner';
import { EvidenceHighlight } from '../components/EvidenceHighlight';
import { GuidanceCard } from '../components/GuidanceCard';
import { ErrorBanner } from '../components/ErrorBanner';
import { Spinner } from '../components/Spinner';
import { CheckCircle, ExternalLink } from 'lucide-react';

export function ReviewPage() {
  const navigate = useNavigate();
  const { getAssessment, state, setEditedDraft, setReviewerName, setCheckboxChecked, setSaveResult, reset } = useInvestigation();
  const assessment = getAssessment();
  
  const [showDiscardDialog, setShowDiscardDialog] = useState(false);
  
  if (!assessment) {
    navigate('/');
    return null;
  }
  
  const originalDraft = assessment.draft;
  const editedDraft = state.editedDraft ?? originalDraft;
  const draftEdited = editedDraft !== originalDraft;
  
  const allEvidence = [
    ...assessment.indicators.flatMap(i => i.evidence),
    ...assessment.social_engineering.flatMap(i => i.evidence),
  ];
  
  const mutation = useMutation({
    mutationFn: createIncident,
    onSuccess: (result) => {
      setSaveResult(result);
    },
  });
  
  const canSave = state.checkboxChecked && !mutation.isPending;
  
  const handleSave = () => {
    if (!canSave) return;
    
    mutation.mutate({
      approved: true,
      reviewed_by: state.reviewerName?.trim() || undefined,
      draft: editedDraft,
      draft_edited: draftEdited,
      assessment: assessment,
    });
  };
  
  const handleDiscard = () => {
    reset();
    navigate('/');
  };
  
  // Show success state
  if (mutation.isSuccess && state.saveResult) {
    return (
      <AppShell showStepper={true}>
        <div className="max-w-2xl mx-auto">
          <div className="bg-white border border-green-200 rounded-xl p-6 shadow-sm text-center">
            <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
            <h1 className="text-2xl font-semibold text-slate-900 mb-2">Incident Saved</h1>
            <p className="text-slate-600 mb-4">The investigation has been successfully saved.</p>
            
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-4 text-left">
              <div className="space-y-2">
                <div>
                  <span className="text-xs font-medium text-slate-600">Incident ID:</span>
                  <p className="text-sm font-mono text-slate-900">{state.saveResult.id}</p>
                </div>
                <div>
                  <span className="text-xs font-medium text-slate-600">Status:</span>
                  <p className="text-sm text-slate-900">{state.saveResult.status}</p>
                </div>
                {state.reviewerName && (
                  <div>
                    <span className="text-xs font-medium text-slate-600">Reviewed by:</span>
                    <p className="text-sm text-slate-900">{state.reviewerName}</p>
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={() => navigate(`/incidents/${state.saveResult!.id}`)}
                className="flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors min-h-[44px]"
              >
                View in Saved Incidents
                <ExternalLink className="w-4 h-4" />
              </button>
              <button
                onClick={() => { reset(); navigate('/'); }}
                className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors min-h-[44px]"
              >
                Investigate another message
              </button>
            </div>
          </div>
        </div>
      </AppShell>
    );
  }
  
  return (
    <AppShell showStepper={true}>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 mb-4">Review & Save</h1>
        </div>
        
        {mutation.isError && (
          <ErrorBanner
            message={mutation.error instanceof Error ? mutation.error.message : 'An error occurred'}
            onRetry={handleSave}
          />
        )}
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Read-only */}
          <div className="space-y-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Original message</h2>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 mb-3">
                <EvidenceHighlight text={assessment.message} evidences={allEvidence} />
              </div>
              <h3 className="text-sm font-medium text-slate-900 mb-2">Evidence summary</h3>
              <div className="space-y-1">
                {assessment.indicators
                  .filter(i => i.status === 'detected' && i.evidence.length > 0)
                  .flatMap(i => i.evidence)
                  .slice(0, 5)
                  .map((evidence, index) => (
                    <div key={index} className="text-xs text-slate-700 font-mono bg-yellow-50 px-2 py-1 rounded">
                      "{evidence.text}"
                    </div>
                  ))}
              </div>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Guidance</h2>
              <div className="space-y-2">
                {assessment.guidance.map((guidance) => (
                  <GuidanceCard key={guidance.id} guidance={guidance} />
                ))}
              </div>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-3">Assessment</h2>
              <p className="text-sm text-slate-700 mb-3">{assessment.assessment}</p>
              <div className="flex items-center gap-2 mb-3">
                <RiskBadge band={assessment.risk.band} />
              </div>
              <UncertaintyBanner />
              
              <h3 className="text-sm font-medium text-slate-900 mb-2">Next steps</h3>
              <ol className="list-decimal list-inside space-y-1">
                {assessment.next_steps.map((step, index) => (
                  <li key={index} className="text-sm text-slate-700">{step}</li>
                ))}
              </ol>
            </div>
          </div>
          
          {/* Right Column - Editable */}
          <div className="space-y-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-2">User guidance draft</h2>
              <p className="text-xs text-slate-600 mb-3">Nothing is sent automatically; you can edit this draft.</p>
              <textarea
                value={editedDraft}
                onChange={(e) => setEditedDraft(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm min-h-[200px]"
                disabled={mutation.isPending}
              />
            </div>
            
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-4">
              <div>
                <label htmlFor="reviewer" className="block text-sm font-medium text-slate-900 mb-1">
                  Your name or initials (optional)
                </label>
                <input
                  id="reviewer"
                  type="text"
                  value={state.reviewerName || ''}
                  onChange={(e) => setReviewerName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 min-h-[44px]"
                  placeholder="e.g., JD"
                  disabled={mutation.isPending}
                />
              </div>
              
              <label className="flex items-start gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={state.checkboxChecked}
                  onChange={(e) => setCheckboxChecked(e.target.checked)}
                  className="mt-1 w-4 h-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500"
                  disabled={mutation.isPending}
                />
                <span className="text-sm text-slate-700">
                  I have reviewed the evidence and approve saving this incident.
                </span>
              </label>
              
              <button
                onClick={handleSave}
                disabled={!canSave}
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium min-h-[44px] flex items-center justify-center gap-2"
              >
                {mutation.isPending ? (
                  <>
                    <Spinner />
                    Saving...
                  </>
                ) : (
                  'Approve & Save Incident'
                )}
              </button>
              
              <p className="text-xs text-slate-500 text-center">
                The incident ID and status appear only after the database confirms the save.
              </p>
              
              <button
                onClick={() => setShowDiscardDialog(true)}
                disabled={mutation.isPending}
                className="w-full px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors min-h-[44px]"
              >
                Discard
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {showDiscardDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Discard investigation?</h3>
            <p className="text-sm text-slate-600 mb-4">
              This will remove all current investigation data. This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDiscardDialog(false)}
                className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors min-h-[44px]"
              >
                Cancel
              </button>
              <button
                onClick={handleDiscard}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors min-h-[44px]"
              >
                Discard
              </button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
