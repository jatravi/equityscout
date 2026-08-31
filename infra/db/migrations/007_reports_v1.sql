-- Week 6: Verdict + Report generation v1

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    version TEXT NOT NULL DEFAULT 'v1',
    verdict_label TEXT NOT NULL,
    verdict_summary TEXT NOT NULL,
    report_markdown TEXT NOT NULL,
    citation_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- one latest report/version per run for MVP
CREATE UNIQUE INDEX IF NOT EXISTS ux_reports_run_version ON reports(run_id, version);

CREATE INDEX IF NOT EXISTS ix_reports_run_id ON reports(run_id);
CREATE INDEX IF NOT EXISTS ix_reports_created_at ON reports(created_at DESC);