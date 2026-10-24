import { useState } from 'react';
import { MessageCircle } from 'lucide-react';

interface ClarificationPromptProps {
  question: string;
  originalMessage: string;
  onContinue: (answer: string) => void;
  isLoading?: boolean;
}

export function ClarificationPrompt({ question, originalMessage, onContinue, isLoading = false }: ClarificationPromptProps) {
  const [answer, setAnswer] = useState('');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (answer.trim()) {
      onContinue(answer.trim());
    }
  };
  
  return (
    <div className="space-y-4">
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
        <div className="flex items-start gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
            <MessageCircle className="w-4 h-4 text-indigo-700" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-slate-900 mb-1">Agent</p>
            <p className="text-sm text-slate-700">{question}</p>
          </div>
        </div>
      </div>
      
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
        <p className="text-xs font-medium text-slate-600 mb-2">Original message:</p>
        <p className="text-sm text-slate-700 font-mono whitespace-pre-wrap">{originalMessage}</p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label htmlFor="clarification-answer" className="block text-sm font-medium text-slate-900 mb-1">
            Your answer
          </label>
          <input
            id="clarification-answer"
            type="text"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 min-h-[44px]"
            placeholder="Type your answer..."
            disabled={isLoading}
          />
        </div>
        <button
          type="submit"
          disabled={!answer.trim() || isLoading}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors min-h-[44px]"
        >
          {isLoading ? 'Continuing...' : 'Continue'}
        </button>
      </form>
    </div>
  );
}
