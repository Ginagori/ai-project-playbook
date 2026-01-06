"""
Supabase client for AI Project Playbook.
Handles all database operations for shared team knowledge.
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from pathlib import Path

# Load .env file if exists
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = Any

from agent.models.project import ProjectState, Phase


class SupabaseClient:
    """Client for Supabase operations."""

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        team_id: Optional[str] = None
    ):
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_ANON_KEY")
        self.team_id = team_id or os.getenv("PLAYBOOK_TEAM_ID")
        self._client: Optional[Client] = None

    @property
    def client(self) -> Optional[Client]:
        """Lazy initialization of Supabase client."""
        if not SUPABASE_AVAILABLE:
            return None
        if self._client is None and self.url and self.key:
            self._client = create_client(self.url, self.key)
        return self._client

    @property
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return bool(self.client and self.team_id)

    # ==========================================
    # TEAM OPERATIONS
    # ==========================================

    async def get_team(self, team_name: str = "Nivanta AI") -> Optional[Dict]:
        """Get team by name."""
        if not self.client:
            return None
        result = self.client.table("teams").select("*").eq("name", team_name).execute()
        return result.data[0] if result.data else None

    async def get_or_create_team(self, team_name: str = "Nivanta AI") -> str:
        """Get team ID or create if doesn't exist."""
        team = await self.get_team(team_name)
        if team:
            return team["id"]

        result = self.client.table("teams").insert({"name": team_name}).execute()
        return result.data[0]["id"]

    async def add_team_member(
        self,
        team_id: str,
        user_identifier: str,
        display_name: Optional[str] = None,
        role: str = "member"
    ) -> Dict:
        """Add a member to the team."""
        if not self.client:
            return {}

        data = {
            "team_id": team_id,
            "user_identifier": user_identifier,
            "display_name": display_name or user_identifier,
            "role": role
        }
        result = self.client.table("team_members").upsert(data).execute()
        return result.data[0] if result.data else {}

    # ==========================================
    # PROJECT OPERATIONS
    # ==========================================

    async def save_project(self, project: ProjectState) -> bool:
        """Save or update a project."""
        if not self.client or not self.team_id:
            return False

        data = {
            "team_id": self.team_id,
            "session_id": project.session_id,
            "objective": project.objective,
            "project_type": project.project_type,
            "tech_stack": project.tech_stack,
            "current_phase": project.current_phase.value if project.current_phase else "discovery",
            "phase_data": {
                "discovery_answers": project.discovery_answers,
                "discovery_complete": project.discovery_complete,
                "planning_complete": project.planning_complete,
                "current_question_index": project.current_question_index,
            },
            "claude_md": project.claude_md,
            "prd": project.prd,
            "roadmap": project.roadmap,
            "implementation_plans": project.implementation_plans,
            "deployment_configs": project.deployment_configs,
            "is_shared": project.is_shared,
            "created_by": project.created_by,
        }

        # Upsert based on session_id
        result = self.client.table("projects").upsert(
            data,
            on_conflict="session_id"
        ).execute()

        return bool(result.data)

    async def get_project(self, session_id: str) -> Optional[ProjectState]:
        """Get a project by session ID."""
        if not self.client:
            return None

        result = self.client.table("projects").select("*").eq("session_id", session_id).execute()

        if not result.data:
            return None

        row = result.data[0]
        phase_data = row.get("phase_data", {})

        return ProjectState(
            session_id=row["session_id"],
            objective=row["objective"],
            project_type=row.get("project_type"),
            tech_stack=row.get("tech_stack", []),
            current_phase=Phase(row["current_phase"]) if row.get("current_phase") else Phase.DISCOVERY,
            discovery_answers=phase_data.get("discovery_answers", {}),
            discovery_complete=phase_data.get("discovery_complete", False),
            planning_complete=phase_data.get("planning_complete", False),
            current_question_index=phase_data.get("current_question_index", 0),
            claude_md=row.get("claude_md"),
            prd=row.get("prd"),
            roadmap=row.get("roadmap", []),
            implementation_plans=row.get("implementation_plans", {}),
            deployment_configs=row.get("deployment_configs", {}),
            is_shared=row.get("is_shared", True),
            created_by=row.get("created_by"),
        )

    async def save_orchestrator_state(self, state: Any) -> bool:
        """Save full orchestrator state to Supabase.

        Args:
            state: OrchestratorState object from the orchestrator
        """
        if not self.client or not self.team_id:
            return False

        project = state.project
        user = os.getenv("PLAYBOOK_USER", "unknown")

        # Serialize tech_stack
        tech_stack_data = None
        if project.tech_stack:
            tech_stack_data = {
                "frontend": project.tech_stack.frontend,
                "backend": project.tech_stack.backend,
                "database": project.tech_stack.database,
                "auth": project.tech_stack.auth,
                "deployment": project.tech_stack.deployment,
                "extras": project.tech_stack.extras,
            }

        # Serialize features
        features_data = []
        for f in project.features:
            features_data.append({
                "name": f.name,
                "description": f.description,
                "status": f.status,
                "plan": f.plan,
                "files": f.files,
                "tests": f.tests,
            })

        data = {
            "team_id": self.team_id,
            "session_id": project.id,
            "objective": project.objective,
            "project_type": project.project_type.value if project.project_type else None,
            "tech_stack": tech_stack_data,
            "current_phase": project.current_phase.value,
            "phase_data": {
                "user_answers": project.user_answers,
                "mode": project.mode.value,
                "scale": project.scale.value,
                "needs_user_input": project.needs_user_input,
                "current_feature_index": project.current_feature_index,
                "discovery_question_index": state.discovery_question_index,
                "features": features_data,
                "pending_question": project.pending_question,
                "validation_results": project.validation_results,
            },
            "claude_md": project.claude_md,
            "prd": project.prd,
            "deployment_configs": project.deployment_configs,
            "is_shared": True,  # Team projects are always shared
            "created_by": user,
        }

        try:
            result = self.client.table("projects").upsert(
                data,
                on_conflict="session_id"
            ).execute()
            return bool(result.data)
        except Exception as e:
            print(f"Error saving to Supabase: {e}")
            return False

    async def load_orchestrator_state(self, session_id: str) -> Optional[Dict]:
        """Load orchestrator state from Supabase.

        Returns raw dict that can be used to reconstruct OrchestratorState.
        """
        if not self.client:
            return None

        try:
            result = self.client.table("projects").select("*").eq("session_id", session_id).execute()
            if result.data:
                return result.data[0]
        except Exception as e:
            print(f"Error loading from Supabase: {e}")

        return None

    async def list_team_projects(
        self,
        limit: int = 20,
        include_completed: bool = True
    ) -> List[Dict]:
        """List all projects for the team."""
        if not self.client or not self.team_id:
            return []

        query = self.client.table("projects").select("*").eq("team_id", self.team_id)

        if not include_completed:
            query = query.is_("completed_at", "null")

        result = query.order("created_at", desc=True).limit(limit).execute()
        return result.data or []

    async def complete_project(self, session_id: str) -> bool:
        """Mark a project as completed."""
        if not self.client:
            return False

        result = self.client.table("projects").update({
            "completed_at": datetime.utcnow().isoformat()
        }).eq("session_id", session_id).execute()

        return bool(result.data)

    # ==========================================
    # LESSONS LEARNED OPERATIONS
    # ==========================================

    async def add_lesson(
        self,
        category: str,
        title: str,
        description: str,
        recommendation: str,
        context: Optional[str] = None,
        project_types: Optional[List[str]] = None,
        tech_stacks: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        source_project_id: Optional[str] = None,
        contributed_by: Optional[str] = None,
        confidence: float = 0.5
    ) -> Optional[Dict]:
        """Add a new lesson learned."""
        if not self.client or not self.team_id:
            return None

        data = {
            "team_id": self.team_id,
            "category": category,
            "title": title,
            "description": description,
            "recommendation": recommendation,
            "context": context,
            "project_types": project_types or [],
            "tech_stacks": tech_stacks or [],
            "tags": tags or [],
            "source_project_id": source_project_id,
            "contributed_by": contributed_by,
            "confidence": confidence
        }

        result = self.client.table("lessons_learned").insert(data).execute()
        return result.data[0] if result.data else None

    async def get_lessons(
        self,
        category: Optional[str] = None,
        project_type: Optional[str] = None,
        tech_stack: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get lessons with optional filtering."""
        if not self.client or not self.team_id:
            return []

        query = self.client.table("lessons_learned").select("*").eq("team_id", self.team_id)

        if category:
            query = query.eq("category", category)

        if project_type:
            query = query.contains("project_types", [project_type])

        if tech_stack:
            # Match any of the tech stacks
            query = query.overlaps("tech_stacks", tech_stack)

        result = query.order("confidence", desc=True).limit(limit).execute()
        return result.data or []

    async def get_lessons_stats(self) -> Dict:
        """Get statistics about lessons."""
        if not self.client or not self.team_id:
            return {"total": 0, "by_category": {}}

        result = self.client.table("lessons_learned").select("category").eq("team_id", self.team_id).execute()

        lessons = result.data or []
        by_category = {}
        for lesson in lessons:
            cat = lesson["category"]
            by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "total": len(lessons),
            "by_category": by_category
        }

    async def vote_lesson(self, lesson_id: str, upvote: bool = True) -> bool:
        """Upvote or downvote a lesson."""
        if not self.client:
            return False

        # Get current votes
        result = self.client.table("lessons_learned").select("upvotes, downvotes").eq("id", lesson_id).execute()
        if not result.data:
            return False

        current = result.data[0]
        update_data = {}

        if upvote:
            update_data["upvotes"] = current["upvotes"] + 1
        else:
            update_data["downvotes"] = current["downvotes"] + 1

        self.client.table("lessons_learned").update(update_data).eq("id", lesson_id).execute()
        return True

    async def increment_lesson_frequency(self, lesson_id: str) -> bool:
        """Increment the frequency counter when a lesson is applied."""
        if not self.client:
            return False

        result = self.client.table("lessons_learned").select("frequency").eq("id", lesson_id).execute()
        if not result.data:
            return False

        new_freq = result.data[0]["frequency"] + 1
        self.client.table("lessons_learned").update({"frequency": new_freq}).eq("id", lesson_id).execute()
        return True

    # ==========================================
    # PROJECT OUTCOMES OPERATIONS
    # ==========================================

    async def save_outcome(
        self,
        project_id: str,
        user_rating: int,
        success_score: float,
        phases_completed: List[str],
        features_completed: int,
        features_planned: int,
        what_worked: Optional[List[str]] = None,
        what_didnt_work: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> Optional[Dict]:
        """Save project outcome for learning."""
        if not self.client or not self.team_id:
            return None

        # First get the project UUID from session_id
        project_result = self.client.table("projects").select("id").eq("session_id", project_id).execute()
        if not project_result.data:
            return None

        project_uuid = project_result.data[0]["id"]

        data = {
            "project_id": project_uuid,
            "team_id": self.team_id,
            "user_rating": user_rating,
            "success_score": success_score,
            "phases_completed": phases_completed,
            "features_completed": features_completed,
            "features_planned": features_planned,
            "what_worked": what_worked or [],
            "what_didnt_work": what_didnt_work or [],
            "notes": notes
        }

        result = self.client.table("project_outcomes").insert(data).execute()
        return result.data[0] if result.data else None

    async def get_similar_outcomes(
        self,
        project_type: str,
        tech_stack: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Find similar project outcomes for recommendations."""
        if not self.client or not self.team_id:
            return []

        # Get projects with matching type
        query = self.client.table("project_summary").select("*").eq("team_id", self.team_id).eq("project_type", project_type)

        result = query.order("success_score", desc=True).limit(limit).execute()
        return result.data or []


# Singleton instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client(force_reload: bool = False) -> SupabaseClient:
    """Get or create the Supabase client singleton.

    Args:
        force_reload: If True, recreate the client with fresh env vars
    """
    global _supabase_client
    if _supabase_client is None or force_reload:
        _supabase_client = SupabaseClient()
    return _supabase_client


def configure_supabase(
    url: str,
    key: str,
    team_id: str
) -> SupabaseClient:
    """Configure and return the Supabase client."""
    global _supabase_client
    _supabase_client = SupabaseClient(url=url, key=key, team_id=team_id)
    return _supabase_client
