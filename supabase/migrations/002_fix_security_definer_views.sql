-- Migration: Fix SECURITY DEFINER views
-- Date: 2026-01-15
-- Issue: Supabase Security Advisor flagged two views with SECURITY DEFINER
-- Solution: Recreate views with SECURITY INVOKER to respect RLS policies

-- Drop existing views
DROP VIEW IF EXISTS public.team_lessons_stats;
DROP VIEW IF EXISTS public.project_summary;

-- Recreate team_lessons_stats with SECURITY INVOKER
CREATE VIEW public.team_lessons_stats
WITH (security_invoker = true)
AS
SELECT
    l.*,
    t.name as team_name,
    (l.upvotes - l.downvotes) as net_votes,
    (l.confidence * l.frequency * (1 + (l.upvotes - l.downvotes) * 0.1)) as relevance_score
FROM lessons_learned l
JOIN teams t ON l.team_id = t.id;

-- Recreate project_summary with SECURITY INVOKER
CREATE VIEW public.project_summary
WITH (security_invoker = true)
AS
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

-- Grant necessary permissions
GRANT SELECT ON public.team_lessons_stats TO anon, authenticated;
GRANT SELECT ON public.project_summary TO anon, authenticated;
