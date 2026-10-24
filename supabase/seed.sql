-- Synthetic seed data (demo only)

-- Trusted domains
INSERT INTO trusted_domains (domain, reason) VALUES
('example.com', 'Synthetic trusted domain for demo'),
('trusted.example', 'Synthetic trusted domain for demo'),
('company.example', 'Synthetic trusted domain for demo')
ON CONFLICT (domain) DO NOTHING;

-- Domain reputation (synthetic)
INSERT INTO domain_reputation (hostname, status, source, reason) VALUES
('suspicious.example', 'suspicious', 'synthetic_demo', 'Synthetic demo entry - flagged pattern'),
('phishy.example', 'suspicious', 'synthetic_demo', 'Synthetic demo entry - suspicious indicators'),
('unknown-site.example', 'unknown', 'synthetic_demo', 'Synthetic demo entry - no data'),
('trusted.example', 'known_trusted', 'synthetic_demo', 'Synthetic trusted domain'),
('example.com', 'known_trusted', 'synthetic_demo', 'Synthetic trusted domain'),
('company.example', 'known_trusted', 'synthetic_demo', 'Synthetic trusted domain')
ON CONFLICT (hostname) DO NOTHING;

-- Guidance passages with stable IDs
INSERT INTO guidance_passages (id, title, content, excerpt) VALUES
('SEC-01', 'Verify sender identity', 'Always verify the sender through a separate channel before taking action on urgent requests. Attackers often impersonate trusted contacts.', 'Verify sender through a separate channel.'),
('SEC-02', 'Be cautious with urgent requests', 'Urgency and pressure are common social engineering tactics. Take time to verify before clicking links or providing credentials.', 'Urgency is a common red flag.'),
('SEC-03', 'Inspect URLs carefully', 'Check URLs for misspellings, unusual domains, and user-info tricks. Do not trust display text alone.', 'Inspect URLs for anomalies.'),
('SEC-04', 'Never share credentials via email/SMS', 'Legitimate organizations will not ask for passwords or MFA codes via email or text message.', 'Never share credentials via message.'),
('SEC-05', 'Report suspicious messages', 'Report suspected phishing to your security team. Preserve the message for investigation.', 'Report and preserve suspicious messages.'),
('SEC-06', 'Use official channels for payments', 'Always confirm payment changes through official channels. Attackers often request urgent payment redirects.', 'Confirm payment changes via official channels.')
ON CONFLICT (id) DO NOTHING;
