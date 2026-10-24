import { ActivityEntry } from '../types/api';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';
import { formatDate } from '../lib/format';

interface ActivityLogProps {
  activities: ActivityEntry[];
}

export function ActivityLog({ activities }: ActivityLogProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set());
  
  const toggleItem = (index: number) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedItems(newExpanded);
  };
  
  if (activities.length === 0) {
    return null;
  }
  
  return (
    <div className="border border-slate-200 rounded-lg">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 hover:bg-slate-50 transition-colors min-h-[44px]"
        aria-expanded={isExpanded}
      >
        <span className="text-sm font-medium text-slate-900">Activity Log</span>
        {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>
      
      {isExpanded && (
        <div className="border-t border-slate-200 divide-y divide-slate-100">
          {activities.map((activity, index) => (
            <div key={index} className="p-3">
              <div className="flex items-start gap-2 mb-1">
                <span className="text-xs text-slate-500 flex-shrink-0">
                  {formatDate(activity.at)}
                </span>
                <span className="text-xs px-1.5 py-0.5 bg-slate-100 text-slate-700 rounded">
                  {activity.kind}
                </span>
                {activity.tool_name && (
                  <span className="text-xs font-mono text-slate-600">{activity.tool_name}</span>
                )}
              </div>
              <p className="text-sm text-slate-900 mb-1">{activity.summary}</p>
              {activity.payload !== undefined && (
                <div>
                  <button
                    onClick={() => toggleItem(index)}
                    className="text-xs text-indigo-600 hover:text-indigo-700 flex items-center gap-1 min-h-[44px]"
                  >
                    {expandedItems.has(index) ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                    {expandedItems.has(index) ? 'Hide' : 'Show'} payload
                  </button>
                  {expandedItems.has(index) && (
                    <pre className="text-xs bg-slate-50 p-2 rounded mt-1 overflow-x-auto border border-slate-200">
                      {JSON.stringify(activity.payload, null, 2)}
                    </pre>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
