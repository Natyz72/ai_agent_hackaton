import { UrlItem } from '../types/api';
import { Copy } from 'lucide-react';
import { useState } from 'react';

interface UrlListProps {
  urls: UrlItem[];
}

// HARD RULES: URLs are shown DEFANGED (http -> hxxp, "." -> "[.]" in hosts) as plain, non-clickable text.
// Never fetch, opens, or links to any URL from a message
export function UrlList({ urls }: UrlListProps) {
  const [copied, setCopied] = useState(false);
  
  const copyDefanged = async () => {
    const defangedList = urls.map(u => u.defanged).join('\n');
    try {
      await navigator.clipboard.writeText(defangedList);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Ignore copy errors
    }
  };
  
  if (urls.length === 0) {
    return (
      <div className="text-sm text-slate-600 italic">No URLs extracted</div>
    );
  }
  
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-medium text-slate-900">Extracted URLs</h4>
        <button
          onClick={copyDefanged}
          className="inline-flex items-center gap-1.5 px-2 py-1 text-xs text-slate-700 hover:bg-slate-100 rounded-md transition-colors min-h-[44px]"
          aria-label="Copy indicators"
        >
          <Copy className="w-3.5 h-3.5" />
          {copied ? 'Copied' : 'Copy indicators'}
        </button>
      </div>
      <ul className="space-y-2">
        {urls.map((url, index) => (
          <li key={index} className="font-mono text-xs text-slate-700 bg-slate-50 p-2 rounded border border-slate-200 break-all">
            {url.defanged}
          </li>
        ))}
      </ul>
    </div>
  );
}
