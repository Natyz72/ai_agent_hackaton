// HARD RULES: URLs are shown DEFANGED (http -> hxxp, "." -> "[.]" in hosts) as plain, non-clickable text.
export function defangUrl(raw: string): string {
  try {
    // Basic defanging: replace http with hxxp and dots in host with [.]
    let defanged = raw.replace(/^http:\/\//i, 'hxxp://').replace(/^https:\/\//i, 'hxxps://');
    
    // Replace dots in the hostname part with [.]
    // Find the host part
    const match = defanged.match(/^(hxxps?:\/\/)([^\/\?#]+)(.*)$/i);
    if (match) {
      const scheme = match[1];
      const host = match[2];
      const rest = match[3];
      const defangedHost = host.replace(/\./g, '[.]');
      return scheme + defangedHost + rest;
    }
    
    return defanged.replace(/\./g, '[.]');
  } catch {
    return raw.replace(/^http/i, 'hxxp').replace(/\./g, '[.]');
  }
}

export function extractUrls(text: string): string[] {
  const urlRegex = /(https?:\/\/[^\s<>"{}|\\^`\[\]]+)/gi;
  const matches = text.match(urlRegex);
  return matches || [];
}
