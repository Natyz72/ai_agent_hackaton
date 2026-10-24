import { Evidence } from '../types/api';

// HARD RULES: Render ALL message text and model output as plain text. Never use dangerouslySetInnerHTML.
// Evidence highlighting must be done by splitting the string by character offsets and wrapping segments in <mark>.
// EvidenceHighlight must apply all evidence offsets from indicators and social_engineering; merges overlapping ranges.
export function mergeEvidenceRanges(evidences: Evidence[]): Array<{ start: number; end: number }> {
  if (evidences.length === 0) return [];
  
  // Create ranges
  const ranges = evidences
    .filter(e => e.end > e.start && e.end > 0)
    .map(e => ({ start: Math.max(0, e.start), end: e.end }))
    .sort((a, b) => {
      if (a.start !== b.start) return a.start - b.start;
      return a.end - b.end;
    });
  
  if (ranges.length === 0) return [];
  
  const merged: Array<{ start: number; end: number }> = [{ ...ranges[0] }];
  
  for (let i = 1; i < ranges.length; i++) {
    const last = merged[merged.length - 1];
    const current = ranges[i];
    
    // Check if overlapping (overlap if current.start <= last.end)
    if (current.start <= last.end) {
      // Merge
      last.end = Math.max(last.end, current.end);
    } else {
      merged.push({ ...current });
    }
  }
  
  return merged;
}

export function splitTextByRanges(text: string, ranges: Array<{ start: number; end: number }>): Array<{ text: string; highlighted: boolean }> {
  if (ranges.length === 0) {
    return [{ text, highlighted: false }];
  }
  
  const segments: Array<{ text: string; highlighted: boolean }> = [];
  let currentIndex = 0;
  
  // Filter ranges within text bounds
  const validRanges = ranges
    .filter(r => r.end > currentIndex && r.start < text.length)
    .map(r => ({
      start: Math.max(0, r.start),
      end: Math.min(text.length, r.end)
    }))
    .sort((a, b) => a.start - b.start);
  
  for (const range of validRanges) {
    // Add text before highlight
    if (range.start > currentIndex) {
      segments.push({
        text: text.substring(currentIndex, range.start),
        highlighted: false
      });
    }
    
    // Add highlighted text
    if (range.start < range.end) {
      segments.push({
        text: text.substring(range.start, range.end),
        highlighted: true
      });
    }
    
    currentIndex = Math.max(currentIndex, range.end);
  }
  
  // Add remaining text
  if (currentIndex < text.length) {
    segments.push({
      text: text.substring(currentIndex),
      highlighted: false
    });
  }
  
  return segments;
}
