import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { AppShell } from '../components/layout/AppShell';
import { sampleMessages } from '../data/sampleMessages';
import { investigateMessage } from '../api/investigate';
import { useInvestigation } from '../state/InvestigationContext';
import { ErrorBanner } from '../components/ErrorBanner';
import { NoticeBanner } from '../components/NoticeBanner';
import { ClarificationPrompt } from '../components/ClarificationPrompt';
import { ChevronDown, ChevronRight } from 'lucide-react';

export function InvestigatePage() {
  const navigate = useNavigate();
  const { state, setMessage, setOptionalDetails, setResponse } = useInvestigation();
  
  const [message, setMessageLocal] = useState(state.message);
  const [sender, setSender] = useState(state.sender || '');
  const [displayName, setDisplayName] = useState(state.display_name || '');
  const [headers, setHeaders] = useState(state.headers || '');
  const [showOptional, setShowOptional] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  
  const mutation = useMutation({
    mutationFn: investigateMessage,
    onSuccess: (response) => {
      setResponse(response);
      if (response.type === 'assessment') {
        navigate('/results');
      }
      // If clarification, stay on page
    },
  });
  
  const isValid = message.trim().length > 0 && message.length <= 3000;
  
  const handleSampleClick = (sampleMsg: string) => {
    setMessageLocal(sampleMsg);
    setMessage(sampleMsg);
  };
  
  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setMessageLocal(value);
    setMessage(value);
  };
  
  const handleAnalyze = () => {
    if (!isValid) return;
    
    // Update optional details in context
    setOptionalDetails({ sender, display_name: displayName, headers });
    
    // Start progress animation
    setProgressStep(1);
    const interval = setInterval(() => {
      setProgressStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 400);
    
    mutation.mutate(
      { 
        message: message.trim(), 
        sender: sender.trim() || undefined,
        display_name: displayName.trim() || undefined,
        headers: headers.trim() || undefined,
      },
      {
        onSettled: () => {
          clearInterval(interval);
          setProgressStep(0);
        },
      }
    );
  };
  
  const handleClarificationContinue = (answer: string) => {
    setOptionalDetails({ sender, display_name: displayName, headers });
    setProgressStep(1);
    const interval = setInterval(() => {
      setProgressStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 400);
    
    mutation.mutate(
      { 
        message: message.trim(),
        sender: sender.trim() || undefined,
        display_name: displayName.trim() || undefined,
        headers: headers.trim() || undefined,
        clarification_answer: answer,
      },
      {
        onSettled: () => {
          clearInterval(interval);
          setProgressStep(0);
        },
      }
    );
  };
  
  const progressSteps = [
    "Inspecting indicators",
    "Checking URLs and language", 
    "Searching guidance",
    "Drafting assessment"
  ];
  
  return (
    <AppShell showStepper={true}>
      <div className="max-w-3xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-slate-900 mb-2">New investigation</h1>
          <p className="text-sm text-slate-600">
            Analyze suspicious messages for phishing and social engineering indicators
          </p>
        </div>
        
        {mutation.isError && (
          <ErrorBanner
            message={mutation.error instanceof Error ? mutation.error.message : 'An error occurred'}
            onRetry={handleAnalyze}
          />
        )}
        
        {mutation.data?.type === 'clarification' ? (
          <ClarificationPrompt
            question={mutation.data.question}
            originalMessage={message}
            onContinue={handleClarificationContinue}
            isLoading={mutation.isPending}
          />
        ) : (
          <div className="space-y-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <label className="block text-sm font-medium text-slate-900 mb-2">
                Sample messages (fictitious)
              </label>
              <div className="flex flex-wrap gap-2">
                {sampleMessages.map((sample) => (
                  <button
                    key={sample.id}
                    onClick={() => handleSampleClick(sample.message)}
                    className="px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md transition-colors min-h-[44px]"
                  >
                    {sample.label}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <label htmlFor="message" className="block text-sm font-medium text-slate-900 mb-1">
                Suspicious message
              </label>
              <textarea
                id="message"
                value={message}
                onChange={handleMessageChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm min-h-[120px]"
                placeholder="Paste the suspicious message here..."
                disabled={mutation.isPending}
              />
              <div className="flex justify-between items-center mt-1">
                <div className="text-xs text-slate-500">
                  {message.length} / 3000
                </div>
                {message.length > 3000 && (
                  <div className="text-xs text-red-600">Message too long</div>
                )}
                {message.trim().length === 0 && message.length > 0 && (
                  <div className="text-xs text-red-600">Message cannot be empty</div>
                )}
              </div>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm">
              <button
                onClick={() => setShowOptional(!showOptional)}
                className="w-full flex items-center justify-between p-4 hover:bg-slate-50 transition-colors min-h-[44px]"
                aria-expanded={showOptional}
              >
                <span className="text-sm font-medium text-slate-900">Optional details</span>
                {showOptional ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </button>
              
              {showOptional && (
                <div className="px-4 pb-4 space-y-3 border-t border-slate-200 pt-3">
                  <div>
                    <label htmlFor="sender" className="block text-sm font-medium text-slate-900 mb-1">
                      Sender address
                    </label>
                    <input
                      id="sender"
                      type="text"
                      value={sender}
                      onChange={(e) => setSender(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 min-h-[44px]"
                      placeholder="e.g., suspicious@example.com"
                      disabled={mutation.isPending}
                    />
                  </div>
                  <div>
                    <label htmlFor="displayName" className="block text-sm font-medium text-slate-900 mb-1">
                      Display name
                    </label>
                    <input
                      id="displayName"
                      type="text"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 min-h-[44px]"
                      placeholder="e.g., IT Support"
                      disabled={mutation.isPending}
                    />
                  </div>
                  <div>
                    <label htmlFor="headers" className="block text-sm font-medium text-slate-900 mb-1">
                      Headers
                    </label>
                    <textarea
                      id="headers"
                      value={headers}
                      onChange={(e) => setHeaders(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm min-h-[80px]"
                      placeholder="Email headers..."
                      disabled={mutation.isPending}
                    />
                  </div>
                </div>
              )}
            </div>
            
            <NoticeBanner message="Links are extracted as text and are never opened. Analysis is text-only." />
            
            {mutation.isPending && progressStep > 0 ? (
              <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
                <p className="text-sm font-medium text-slate-900 mb-3">Analyzing message...</p>
                <ul className="space-y-2">
                  {progressSteps.map((step, index) => (
                    <li key={index} className="flex items-center gap-2 text-sm">
                      <div
                        className={`w-2 h-2 rounded-full ${
                          index + 1 <= progressStep ? 'bg-indigo-600' : 'bg-slate-300'
                        }`}
                      />
                      <span className={index + 1 <= progressStep ? 'text-slate-900' : 'text-slate-500'}>
                        {step}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <button
                onClick={handleAnalyze}
                disabled={!isValid || mutation.isPending}
                className="w-full px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium min-h-[44px]"
              >
                Analyze Message
              </button>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
