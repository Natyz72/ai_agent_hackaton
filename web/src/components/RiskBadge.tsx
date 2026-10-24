import { RiskBand } from '../types/api';

interface RiskBadgeProps {
  band: RiskBand;
}

export function RiskBadge({ band }: RiskBadgeProps) {
  const getStyles = () => {
    switch (band) {
      case 'High':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'Suspicious':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'Low / Inconclusive':
        return 'bg-slate-100 text-slate-700 border-slate-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium border ${getStyles()}`}>
      {band}
    </span>
  );
}
