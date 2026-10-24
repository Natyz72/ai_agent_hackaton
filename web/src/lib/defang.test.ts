import { describe, it, expect } from 'vitest';
import { defangUrl } from './defang';

describe('defangUrl', () => {
  it('defangs http to hxxp', () => {
    expect(defangUrl('http://example.com')).toBe('hxxp://example[.]com');
  });

  it('defangs https to hxxps', () => {
    expect(defangUrl('https://example.com/path')).toBe('hxxps://example[.]com/path');
  });

  it('replaces dots in hostname with [.]', () => {
    expect(defangUrl('https://sub.example.com')).toBe('hxxps://sub[.]example[.]com');
  });
});
