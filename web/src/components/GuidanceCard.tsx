import { GuidanceRef } from '../types/api';

interface GuidanceCardProps {
  guidance: GuidanceRef;
}

export function GuidanceCard({ guidance }: GuidanceCardProps) {
  return (
    <div className="border border-slate-200 rounded-lg p-3 mb-2 bg-white">
      <div className="flex items-start gap-2">
        <span className="text-xs font-mono text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded flex-shrink-0">
          {guidance.id}
        </span>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-slate-900 mb-1">{guidance.title}</h4>
          <p className="text-xs text-slate-700">{guidance.excerpt}</p>
        </div>
      </div>
    </div>
  );
}
