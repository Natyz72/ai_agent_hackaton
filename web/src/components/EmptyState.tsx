import { FileX } from 'lucide-react';

interface EmptyStateProps {
  message: string;
}

export function EmptyState({ message }: EmptyStateProps) {
  return (
    <div className="text-center py-12">
      <FileX className="w-12 h-12 text-slate-400 mx-auto mb-3" />
      <p className="text-slate-600">{message}</p>
    </div>
  );
}
