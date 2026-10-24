import { Evidence } from '../types/api';
import { mergeEvidenceRanges, splitTextByRanges } from '../lib/highlight';

interface EvidenceHighlightProps {
  text: string;
  evidences: Evidence[];
  className?: string;
}

// HARD RULES: Render ALL message text and model output as plain text. Never use dangerouslySetInnerHTML.
// Evidence highlighting must be done by splitting the string by character offsets and wrapping segments in <mark>.
// Merges overlapping ranges
export function EvidenceHighlight({ text, evidences, className = '' }: EvidenceHighlightProps) {
  const ranges = mergeEvidenceRanges(evidences);
  const segments = splitTextByRanges(text, ranges);
  
  return (
    <div className={`font-mono text-sm whitespace-pre-wrap break-words ${className}`}>
      {segments.map((segment, index) => (
        segment.highlighted ? (
          <mark key={index}>{segment.text}</mark>
        ) : (
          <span key={index}>{segment.text}</span>
        )
      ))}
    </div>
  );
}
