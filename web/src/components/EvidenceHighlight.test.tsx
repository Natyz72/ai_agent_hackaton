import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { EvidenceHighlight } from './EvidenceHighlight';

describe('EvidenceHighlight', () => {
  it('highlights text at offsets', () => {
    const text = 'Hello world';
    const evidences = [{ start: 6, end: 11, text: 'world', source: 'test' }];
    const { container } = render(<EvidenceHighlight text={text} evidences={evidences as any} />);
    const mark = container.querySelector('mark');
    expect(mark?.textContent).toBe('world');
  });
});
