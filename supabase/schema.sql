-- AI Suspicious Message Investigation Agent Schema

-- Trusted domains
CREATE TABLE IF NOT EXISTS trusted_domains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain TEXT UNIQUE NOT NULL,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Domain reputation (synthetic)
CREATE TABLE IF NOT EXISTS domain_reputation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hostname TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('known_trusted', 'suspicious', 'unknown')),
    source TEXT,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Guidance passages (handbook)
CREATE TABLE IF NOT EXISTS guidance_passages (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Investigation proposals (pending approval) - NOT incidents
CREATE TABLE IF NOT EXISTS investigation_proposals (
    id UUID PRIMARY KEY,
    status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'used')),
    message TEXT NOT NULL,
    output_snapshot JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Incidents (saved only after approval)
CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID,
    message TEXT NOT NULL,
    findings JSONB,
    risk JSONB,
    guidance_draft TEXT,
    guidance JSONB,
    url_analysis JSONB,
    attack_sequence JSONB,
    analyst_notes TEXT,
    status TEXT DEFAULT 'saved',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Activity log
CREATE TABLE IF NOT EXISTS activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID,
    proposal_id UUID,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    detail JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE trusted_domains ENABLE ROW LEVEL SECURITY;
ALTER TABLE domain_reputation ENABLE ROW LEVEL SECURITY;
ALTER TABLE guidance_passages ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;

-- No anonymous/public write policies - service role only
CREATE POLICY "service_role_all_trusted" ON trusted_domains FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_all_reputation" ON domain_reputation FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_all_guidance" ON guidance_passages FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_all_proposals" ON investigation_proposals FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_all_incidents" ON incidents FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_all_activity" ON activity_log FOR ALL USING (auth.role() = 'service_role');
