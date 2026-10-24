import { AttackStep } from '../types/api';
import { ArrowRight } from 'lucide-react';

interface AttackSequenceProps {
  steps: AttackStep[];
}

export function AttackSequence({ steps }: AttackSequenceProps) {
  if (steps.length === 0) {
    return (
      <div className="text-sm text-slate-600 italic">No attack sequence inferred</div>
    );
  }
  
  return (
    <div>
      <div className="space-y-3">
        {steps.map((step, index) => (
          <div key={index} className="flex gap-3">
            <div className="flex flex-col items-center">
              <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-medium flex-shrink-0">
                {index + 1}
              </div>
              {index < steps.length - 1 && (
                <ArrowRight className="w-4 h-4 text-slate-400 mt-1 rotate-90" />
              )}
            </div>
            <div className="flex-1 pb-4">
              <p className="text-sm text-slate-900 mb-1">{step.step}</p>
              {step.evidence.length > 0 && (
                <div className="text-xs text-slate-600 font-mono bg-slate-50 p-2 rounded border border-slate-200">
                  {step.evidence.map((e, i) => (
                    <div key={i}>"{e.text}"</div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-slate-500 italic mt-2">
        Inferred from message text; does not prove what the recipient did.
      </p>
    </div>
  );
}
