import { describe, it, expect } from 'vitest';
import { mergeEvidenceRanges, splitTextByRanges } from './highlight';

describe('mergeEvidenceRanges', () => {
  it('merges overlapping ranges', () => {
    const ranges = [
      { start: 0, end: 10 },
      { start: 5, end: 15 },
    ];
    const merged = mergeEvidenceRanges(ranges as any);
    expect(merged).toEqual([{ start: 0, end: 15 }]);
  });

  it('handles bounds cases', () => {
    const ranges = [
      { start: -1, end: 5 },
      { start: 10, end: 3 }, // end < start
    ];
    const merged = mergeEvidenceRanges(ranges as any);
    expect(merged).toEqual([{ start: 0, end: 5 }]);
  });
});
