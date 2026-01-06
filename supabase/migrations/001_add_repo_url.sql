-- Migration: Add repo_url to projects table
-- Run this in Supabase SQL Editor

ALTER TABLE projects ADD COLUMN IF NOT EXISTS repo_url TEXT;

-- Optional: Add index for faster lookups by repo
CREATE INDEX IF NOT EXISTS idx_projects_repo_url ON projects(repo_url);

-- Comment for documentation
COMMENT ON COLUMN projects.repo_url IS 'GitHub repository URL for the project';
