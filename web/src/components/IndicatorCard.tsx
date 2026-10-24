import { Indicator } from '../types/api';
import { AlertCircle, CheckCircle, XCircle } from 'lucide-react';

interface IndicatorCardProps {
  indicator: Indicator;
}

// HARD RULES: Indicator status has exactly three states and each must look different:
// detected | not_detected | not_assessable (with a reason shown).
// Status is NEVER color alone: always include a text label (and icon).
export function IndicatorCard({ indicator }: IndicatorCardProps) {
  const getStatusConfig = () => {
    switch (indicator.status) {
      case 'detected':
        return {
          icon: <AlertCircle className="w-4 h-4" />,
          label: 'Detected',
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-700',
          iconColor: 'text-red-700'
        };
      case 'not_detected':
        return {
          icon: <CheckCircle className="w-4 h-4" />,
          label: 'Not detected',
          bg: 'bg-slate-50',
          border: 'border-slate-200',
          text: 'text-slate-700',
          iconColor: 'text-slate-600'
        };
      case 'not_assessable':
        return {
          icon: <XCircle className="w-4 h-4" />,
          label: 'Not assessable',
          bg: 'bg-slate-50',
          border: 'border-dashed border-slate-300',
          text: 'text-slate-600',
          iconColor: 'text-slate-500'
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={`border rounded-lg p-3 mb-2 ${config.bg} ${config.border}`}>
      <div className="flex items-start gap-2">
        <div className={`flex-shrink-0 ${config.iconColor}`}>{config.icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <h4 className="text-sm font-medium text-slate-900">{indicator.label}</h4>
            <span className={`text-xs font-medium ${config.text} flex items-center gap-1`}>
              {config.icon}
              {config.label}
            </span>
          </div>
          {indicator.status === 'not_assessable' && indicator.reason && (
            <p className="text-xs text-slate-600 mt-1">{indicator.reason}</p>
          )}
          <p className="text-xs text-slate-500 mt-1 font-mono">Tool: {indicator.tool}</p>
        </div>
      </div>
    </div>
  );
}
