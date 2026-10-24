import { Info } from 'lucide-react';

interface NoticeBannerProps {
  message: string;
}

export function NoticeBanner({ message }: NoticeBannerProps) {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start gap-2" role="note">
      <Info className="w-4 h-4 text-blue-700 flex-shrink-0 mt-0.5" />
      <p className="text-sm text-blue-900">{message}</p>
    </div>
  );
}
