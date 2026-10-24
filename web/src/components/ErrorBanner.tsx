import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4" role="alert" aria-live="assertive">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-red-700 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-sm text-red-900 font-medium mb-2">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm bg-red-100 hover:bg-red-200 text-red-900 rounded-md transition-colors min-h-[44px]"
            >
              <RefreshCw className="w-4 h-4" />
              Retry
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
