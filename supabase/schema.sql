-- AI Project Playbook - Supabase Schema
-- Run this in the SQL Editor after creating your project

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TEAMS TABLE (for Nivanta AI team members)
-- ============================================
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert Nivanta AI team
INSERT INTO teams (name) VALUES ('Nivanta AI');

-- ============================================
-- TEAM MEMBERS (who belongs to which team)
-- ============================================
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    user_identifier TEXT NOT NULL, -- Can be email, API key, or machine ID
    display_name TEXT,
    role TEXT DEFAULT 'member', -- 'admin', 'member'
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(team_id, user_identifier)
);

-- ============================================
-- PROJECTS TABLE
-- ============================================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    session_id TEXT UNIQUE NOT NULL,
    objective TEXT NOT NULL,
    project_type TEXT, -- 'saas', 'api', 'agent', 'multi_agent'
    tech_stack JSONB DEFAULT '[]'::jsonb,
    current_phase TEXT DEFAULT 'discovery',
    phase_data JSONB DEFAULT '{}'::jsonb,

    -- Generated artifacts
    claude_md TEXT,
    prd TEXT,
    roadmap JSONB,
    implementation_plans JSONB,
    deployment_configs JSONB,

    -- Metadata
    is_shared BOOLEAN DEFAULT true,
    created_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- ============================================
-- LESSONS LEARNED (shared knowledge base)
-- ============================================
CREATE TABLE lessons_learned (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,

    category TEXT NOT NULL, -- 'tech_stack', 'architecture', 'workflow', 'tooling', 'testing', 'deployment', 'pitfall'
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    context TEXT,
    recommendation TEXT NOT NULL,

    -- Scoring
    confidence FLOAT DEFAULT 0.5,
    frequency INTEGER DEFAULT 1,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,

    -- Filtering
    project_types TEXT[] DEFAULT '{}',
    tech_stacks TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',

    -- Source
    source_project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    contributed_by TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- PROJECT OUTCOMES (for learning from completed projects)
-- ============================================
CREATE TABLE project_outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,

    -- Ratings
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    success_score FLOAT,

    -- What happened
    phases_completed TEXT[] DEFAULT '{}',
    features_completed INTEGER DEFAULT 0,
    features_planned INTEGER DEFAULT 0,

    -- Learnings
    what_worked TEXT[],
    what_didnt_work TEXT[],
    notes TEXT,

    completed_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES for performance
-- ============================================
CREATE INDEX idx_projects_team ON projects(team_id);
CREATE INDEX idx_projects_session ON projects(session_id);
CREATE INDEX idx_projects_phase ON projects(current_phase);
CREATE INDEX idx_lessons_team ON lessons_learned(team_id);
CREATE INDEX idx_lessons_category ON lessons_learned(category);
CREATE INDEX idx_lessons_project_types ON lessons_learned USING GIN(project_types);
CREATE INDEX idx_lessons_tech_stacks ON lessons_learned USING GIN(tech_stacks);
CREATE INDEX idx_outcomes_project ON project_outcomes(project_id);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE lessons_learned ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_outcomes ENABLE ROW LEVEL SECURITY;

-- Policy: Team members can see their team's data
-- Using service_role key bypasses RLS, so this is for future auth integration

CREATE POLICY "Team members can view their team" ON teams
    FOR SELECT USING (true);

CREATE POLICY "Team members can view members" ON team_members
    FOR SELECT USING (true);

CREATE POLICY "Team members can manage projects" ON projects
    FOR ALL USING (true);

CREATE POLICY "Team members can manage lessons" ON lessons_learned
    FOR ALL USING (true);

CREATE POLICY "Team members can manage outcomes" ON project_outcomes
    FOR ALL USING (true);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_teams_updated_at
    BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_lessons_updated_at
    BEFORE UPDATE ON lessons_learned
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- VIEWS for easy querying
-- ============================================

-- Team lessons with stats
CREATE VIEW team_lessons_stats AS
SELECT
    l.*,
    t.name as team_name,
    (l.upvotes - l.downvotes) as net_votes,
    (l.confidence * l.frequency * (1 + (l.upvotes - l.downvotes) * 0.1)) as relevance_score
FROM lessons_learned l
JOIN teams t ON l.team_id = t.id;

-- Project summary
CREATE VIEW project_summary AS
SELECT
    p.*,
    t.name as team_name,
    po.user_rating,
    po.success_score,
    po.features_completed,
    po.features_planned
FROM projects p
JOIN teams t ON p.team_id = t.id
LEFT JOIN project_outcomes po ON p.id = po.project_id;

-- ============================================
-- SAMPLE DATA (optional - for testing)
-- ============================================

-- Get the Nivanta AI team ID for inserting sample data
-- DO $$
-- DECLARE
--     nivanta_team_id UUID;
-- BEGIN
--     SELECT id INTO nivanta_team_id FROM teams WHERE name = 'Nivanta AI';
--
--     -- Add team members
--     INSERT INTO team_members (team_id, user_identifier, display_name, role)
--     VALUES
--         (nivanta_team_id, 'natalia', 'Natalia', 'admin'),
--         (nivanta_team_id, 'compañero', 'Compañero', 'member');
-- END $$;
