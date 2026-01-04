# Product Requirements Document (PRD) Template

**Product:** [PRODUCT NAME]
**Author:** [YOUR NAME]
**Created:** [DATE]
**Last Updated:** [DATE]
**Status:** [Draft / In Review / Approved / In Development / Completed]

---

## 1. EXECUTIVE SUMMARY

**One-sentence description:**
[Describe the product/feature in one sentence - what it is and who it's for]

**Problem:**
[What problem does this solve? Why does it matter?]

**Solution:**
[High-level solution approach - what we're building]

**Success Metrics:**
- [Metric 1]: [Target - e.g., "50% user adoption in first month"]
- [Metric 2]: [Target]
- [Metric 3]: [Target]

**Target Launch Date:** [DATE or "TBD"]

---

## 2. BACKGROUND & CONTEXT

### 2.1 Why Now?

**What's changed that makes this important now?**
[Market changes, user feedback, business priorities, technical enablers]

**What happens if we don't build this?**
[Consequences of inaction - lost revenue, user churn, competitive disadvantage]

---

### 2.2 Research & Validation

**User Research:**
- [Research method 1]: [Key finding]
- [Research method 2]: [Key finding]
- [Example: "User interviews (n=20): 80% said they struggle with [problem]"]

**Market Analysis:**
- Competitors doing this: [List competitors with similar features]
- Competitors NOT doing this: [Gap in market?]
- Our differentiation: [What makes our approach unique]

**Data/Evidence:**
- [Metric 1]: [Current state - e.g., "Current conversion rate: 2%"]
- [Metric 2]: [Current state]
- [Expected improvement]: [e.g., "Target conversion rate: 5% (+150%)"]

---

## 3. USERS & PERSONAS

### 3.1 Target Users

**Primary User:**
- **Who:** [Description - e.g., "SaaS product managers with 2-5 years experience"]
- **Size:** [How many users - e.g., "~10,000 potential users in our target market"]
- **Current Behavior:** [What do they do today without this feature?]
- **Pain Point:** [Their specific problem this solves]

**Secondary Users:**
- **Who:** [Description]
- **Size:** [How many]
- **Use Case:** [How they'll use it differently from primary users]

---

### 3.2 User Personas

**Persona 1: [Name - e.g., "Project Manager Patricia"]**
- **Demographics:** [Age, role, experience level]
- **Goals:** [What they want to achieve]
- **Frustrations:** [What annoys them about current solutions]
- **Tech Savviness:** [Low / Medium / High]
- **Quote:** "[A representative quote from user research]"

**Persona 2: [Name]**
[Same structure]

---

### 3.3 User Journey (Current State vs. Future State)

**Current Journey (WITHOUT this feature):**
1. [Step 1 - e.g., "User opens dashboard"]
2. [Step 2 - e.g., "Manually exports data to CSV"]
3. [Step 3 - e.g., "Opens Excel, creates charts manually"]
4. [Pain point - e.g., "Takes 30 minutes, error-prone"]

**Future Journey (WITH this feature):**
1. [Step 1 - e.g., "User opens dashboard"]
2. [Step 2 - e.g., "Clicks 'Generate Report' button"]
3. [Step 3 - e.g., "Gets PDF report with charts automatically"]
4. [Benefit - e.g., "Takes 30 seconds, always accurate"]

**Time Saved:** [X minutes/hours per user per week]
**Frustration Eliminated:** [What pain goes away]

---

## 4. PRODUCT GOALS & SUCCESS METRICS

### 4.1 Product Goals

**Primary Goal:**
[Main objective - e.g., "Increase user retention by making onboarding easier"]

**Secondary Goals:**
1. [Goal 2 - e.g., "Reduce support tickets about feature X"]
2. [Goal 3 - e.g., "Enable users to achieve first value in < 5 minutes"]

---

### 4.2 Success Metrics (OKRs)

**Objective 1:** [High-level goal]
- **KR1:** [Measurable result - e.g., "50% of new users complete onboarding"]
- **KR2:** [Measurable result]
- **KR3:** [Measurable result]

**Objective 2:** [High-level goal]
- **KR1:** [Measurable result]
- **KR2:** [Measurable result]

---

### 4.3 How We'll Measure

**Instrumentation Needed:**
- [Event 1]: [What we'll track - e.g., "user_clicked_generate_report"]
- [Event 2]: [What we'll track]
- [Metric 1]: [What we'll measure - e.g., "Time from signup to first report generated"]

**Dashboard:**
- [Where metrics will be tracked - e.g., "Mixpanel dashboard: [link]"]

**Review Cadence:**
- [How often we'll review - e.g., "Weekly during first month, then monthly"]

---

## 5. REQUIREMENTS

### 5.1 User Stories

**Epic 1: [Epic Name]**

**Story 1.1:**
- **As a** [user type]
- **I want to** [action]
- **So that** [benefit]
- **Acceptance Criteria:**
  1. [ ] [Specific criterion - testable]
  2. [ ] [Specific criterion]
  3. [ ] [Specific criterion]
- **Priority:** [P0 / P1 / P2]

**Story 1.2:**
[Same structure]

**Epic 2: [Epic Name]**
[More stories]

---

### 5.2 Functional Requirements

**MUST HAVE (P0 - MVP):**
1. [Requirement 1 - e.g., "User can upload CSV files up to 10MB"]
2. [Requirement 2]
3. [Requirement 3]

**SHOULD HAVE (P1 - Launch +1 month):**
1. [Requirement 1 - e.g., "User can schedule recurring reports"]
2. [Requirement 2]

**COULD HAVE (P2 - Future):**
1. [Requirement 1 - e.g., "Integration with Google Sheets"]
2. [Requirement 2]

**WON'T HAVE (Out of Scope):**
1. [Requirement 1 - e.g., "Real-time collaboration (like Google Docs)"]
2. [Requirement 2]
- **Rationale:** [Why not - e.g., "Too complex for MVP, revisit in 6 months"]

---

### 5.3 Non-Functional Requirements

**Performance:**
- [Requirement 1 - e.g., "Report generation completes in < 5 seconds"]
- [Requirement 2 - e.g., "Page load time < 2 seconds"]

**Scalability:**
- [Requirement 1 - e.g., "Support 10,000 concurrent users"]
- [Requirement 2 - e.g., "Handle 1M reports/month"]

**Security:**
- [Requirement 1 - e.g., "All data encrypted at rest and in transit"]
- [Requirement 2 - e.g., "RBAC - only admins can delete reports"]

**Accessibility:**
- [Requirement 1 - e.g., "WCAG 2.1 AA compliance"]
- [Requirement 2 - e.g., "Keyboard navigation support"]

**Reliability:**
- [Requirement 1 - e.g., "99.9% uptime SLA"]
- [Requirement 2 - e.g., "Zero data loss"]

---

### 5.4 Edge Cases & Error Handling

**Edge Case 1:** [Scenario - e.g., "User uploads malformed CSV"]
- **Expected Behavior:** [What happens - e.g., "Show error message: 'Invalid file format. Please upload a valid CSV.'"]

**Edge Case 2:** [Scenario - e.g., "Report generation takes > 30 seconds"]
- **Expected Behavior:** [What happens - e.g., "Process in background, email user when ready"]

**Edge Case 3:** [Scenario]
- **Expected Behavior:** [What happens]

---

## 6. DESIGN & USER EXPERIENCE

### 6.1 Wireframes / Mockups

**[Link to Figma / Sketch / etc.]**
[Or embed key screens here]

**Screen 1: [Screen Name]**
- **Purpose:** [What this screen does]
- **Key Elements:**
  - [Element 1 - e.g., "Upload button (top right)"]
  - [Element 2 - e.g., "Progress bar during upload"]
- **User Flow:** [How user gets here and where they go next]

**Screen 2: [Screen Name]**
[Same structure]

---

### 6.2 User Flows

**Flow 1: [Flow Name - e.g., "Generate Report"]**
1. User clicks "Generate Report" button
2. Modal opens with report options (date range, format)
3. User selects options, clicks "Generate"
4. Loading spinner appears (5 sec)
5. Report displays in new tab
6. Success message: "Report generated successfully"

**Happy Path:** Steps 1-6 complete successfully
**Error Path:** If step 4 fails → Show error message, option to retry

**Flow 2: [Flow Name]**
[Same structure]

---

### 6.3 Interaction Details

**Button States:**
- Default: [Description or screenshot]
- Hover: [Description]
- Disabled: [Description]
- Loading: [Description]

**Form Validation:**
- [Field 1]: [Validation rules - e.g., "Email must be valid format"]
- [Field 2]: [Validation rules]
- Error messages: [How errors are displayed]

**Loading States:**
- [When]: [What shows - e.g., "Skeleton loader while data fetches"]

**Empty States:**
- [When]: [What shows - e.g., "No reports yet. Click 'Generate Report' to get started."]

---

## 7. TECHNICAL ARCHITECTURE

### 7.1 High-Level Architecture

```
[User Browser]
     ↓
[Frontend - React]
     ↓ (API calls)
[Backend - FastAPI]
     ↓
[Database - PostgreSQL]
     ↓
[Background Jobs - Celery] (for async report generation)
     ↓
[File Storage - S3] (for generated reports)
```

**Rationale for tech choices:**
- [Choice 1]: [Why - e.g., "React: Team already familiar, component reusability"]
- [Choice 2]: [Why]

---

### 7.2 Data Model

**New Tables/Models:**

**Table: reports**
- `id` (UUID, PK)
- `user_id` (UUID, FK to users)
- `name` (VARCHAR(255))
- `status` (ENUM: pending, generating, completed, failed)
- `file_url` (VARCHAR(500), nullable)
- `created_at` (TIMESTAMP)
- `completed_at` (TIMESTAMP, nullable)

**Table: report_templates**
[Same structure]

**Relationships:**
- User → Reports (1:many)
- ReportTemplate → Reports (1:many)

---

### 7.3 API Endpoints

**POST /api/v1/reports**
- **Purpose:** Create new report
- **Auth:** Required (JWT)
- **Request Body:**
  ```json
  {
    "template_id": "uuid",
    "parameters": {
      "date_range": "2025-01-01 to 2025-01-31"
    }
  }
  ```
- **Response (201):**
  ```json
  {
    "id": "uuid",
    "status": "pending",
    "created_at": "2025-01-18T10:00:00Z"
  }
  ```
- **Errors:**
  - 400: Invalid parameters
  - 401: Unauthorized
  - 404: Template not found

**GET /api/v1/reports/{id}**
[Same structure]

**GET /api/v1/reports**
[Same structure]

---

### 7.4 Third-Party Integrations

**Integration 1: [Service Name - e.g., "SendGrid"]**
- **Purpose:** [Why - e.g., "Send email when report is ready"]
- **API:** [Link to docs]
- **Authentication:** [How - e.g., "API key in env var"]
- **Rate Limits:** [Limits - e.g., "100 emails/hour on free tier"]

**Integration 2: [Service Name]**
[Same structure]

---

### 7.5 Security Considerations

**Authentication:**
- [Approach - e.g., "JWT tokens with 24h expiry"]

**Authorization:**
- [Approach - e.g., "Users can only access their own reports"]

**Data Protection:**
- [Approach - e.g., "Reports encrypted at rest (AES-256)"]
- [Approach - e.g., "HTTPS for all API calls"]

**Input Validation:**
- [Approach - e.g., "Pydantic models validate all inputs"]

**Rate Limiting:**
- [Approach - e.g., "Max 10 report generations per user per hour"]

---

## 8. IMPLEMENTATION PLAN

### 8.1 Phases

**Phase 1: MVP (Weeks 1-2)**
- [ ] Backend: Data models + migrations
- [ ] Backend: Report generation service (basic)
- [ ] Backend: API endpoints (POST, GET)
- [ ] Frontend: Report generation form
- [ ] Frontend: Report list view
- [ ] Tests: Unit + Integration

**Phase 2: Enhancements (Weeks 3-4)**
- [ ] Background job processing (Celery)
- [ ] Email notifications
- [ ] Report templates
- [ ] Export to PDF

**Phase 3: Polish (Week 5)**
- [ ] Error handling improvements
- [ ] Loading states
- [ ] Empty states
- [ ] Performance optimization

---

### 8.2 Dependencies & Blockers

**Dependencies:**
- [Dependency 1 - e.g., "AWS S3 bucket must be provisioned by DevOps"]
  - **Owner:** [Who's responsible]
  - **Deadline:** [When needed]
  - **Status:** [Not started / In progress / Done]

**Potential Blockers:**
- [Blocker 1 - e.g., "SendGrid approval process takes 2-3 weeks"]
  - **Mitigation:** [How to work around - e.g., "Start approval process now"]

---

### 8.3 Testing Plan

**Unit Tests:**
- [What to test - e.g., "Report generation logic"]
- Target coverage: [80%+]

**Integration Tests:**
- [What to test - e.g., "Full API flow: create report → fetch report"]

**E2E Tests:**
- [What to test - e.g., "User generates report via UI, receives email, downloads PDF"]

**Performance Tests:**
- [What to test - e.g., "Report generation time < 5 sec for 10k rows"]

**Load Tests:**
- [What to test - e.g., "System handles 100 concurrent report generations"]

**Security Tests:**
- [What to test - e.g., "User A cannot access User B's reports"]

---

### 8.4 Rollout Plan

**Stage 1: Internal Alpha (Week 6)**
- Deploy to staging
- Internal team testing (5-10 users)
- Fix critical bugs

**Stage 2: Beta (Week 7)**
- Deploy to production (feature flag disabled)
- Enable for 10% of users (100 beta testers)
- Monitor metrics, gather feedback
- Fix non-critical bugs

**Stage 3: General Availability (Week 8)**
- Enable for 100% of users
- Announce via email, blog post
- Monitor closely for issues

**Rollback Plan:**
- Feature flag can disable feature instantly if critical issues
- Database migrations have rollback scripts

---

## 9. RISKS & MITIGATIONS

**Risk 1: [Risk Description]**
- **Probability:** [Low / Medium / High]
- **Impact:** [Low / Medium / High]
- **Mitigation:** [How to prevent or reduce risk]
- **Contingency:** [What to do if risk materializes]

**Example:**
**Risk 1: Report generation is too slow (>10 sec)**
- **Probability:** Medium
- **Impact:** High (poor UX, user abandonment)
- **Mitigation:** Performance testing early, optimize queries, add caching
- **Contingency:** Move to background job processing (phase 2 feature pulled into phase 1)

**Risk 2:** [Another risk]
[Same structure]

---

## 10. OPEN QUESTIONS & DECISIONS

**Question 1:** [Open question - e.g., "Should we support Excel export or PDF only?"]
- **Options:**
  - A) PDF only (simpler, faster to build)
  - B) PDF + Excel (more flexible for users)
- **Decision:** [TBD / A / B]
- **Owner:** [Who decides]
- **Deadline:** [When decision needed]

**Question 2:** [Another question]
[Same structure]

---

## 11. OUT OF SCOPE

**Explicitly NOT included in this PRD:**
1. [Feature 1 - e.g., "Real-time collaboration on reports"]
   - **Why:** Too complex for MVP, consider in v2
2. [Feature 2 - e.g., "Custom branding (logos, colors)"]
   - **Why:** Low user demand (only 5% of users requested)
3. [Feature 3]

**Clarify to avoid scope creep.**

---

## 12. APPENDIX

### 12.1 Competitive Analysis

**Competitor 1: [Name]**
- **Their approach:** [How they solve this problem]
- **Strengths:** [What they do well]
- **Weaknesses:** [What they do poorly]
- **Our differentiation:** [How we'll be better]

**Competitor 2: [Name]**
[Same structure]

---

### 12.2 User Research Quotes

**Quote 1:**
> "[Actual user quote from interview]"
> — [User persona type], [Date]

**Quote 2:**
[Another quote]

---

### 12.3 Glossary

**Term 1:** [Definition]
**Term 2:** [Definition]

---

### 12.4 References

- [Research doc]: [Link]
- [Design file]: [Link to Figma]
- [Technical RFC]: [Link]
- [Competitive analysis]: [Link]

---

## CHANGELOG

**[DATE] - [Author]**
- Created initial PRD

**[DATE] - [Author]**
- Updated [section] based on [feedback from whom]

**[DATE] - [Author]**
- Approved by [stakeholder]

---

## APPROVALS

**Product Manager:** [Name] ☐ Approved ☐ Rejected
**Engineering Lead:** [Name] ☐ Approved ☐ Rejected
**Design Lead:** [Name] ☐ Approved ☐ Rejected
**Stakeholder:** [Name] ☐ Approved ☐ Rejected

**Final Approval Date:** [DATE or TBD]

---

## TEMPLATE USAGE INSTRUCTIONS

**How to use this PRD template:**

1. **Copy template** to `docs/prd/[feature-name].md`

2. **Fill all sections** - don't skip, even if "N/A" (explain why N/A)

3. **Be specific** - avoid vague requirements like "fast" or "user-friendly"
   - ❌ Bad: "The system should be fast"
   - ✅ Good: "API response time < 200ms at p95"

4. **Prioritize ruthlessly** - Not everything is P0
   - P0 (Must Have): Feature doesn't work without this
   - P1 (Should Have): Feature works but incomplete
   - P2 (Could Have): Nice-to-have
   - Won't Have: Out of scope

5. **Get feedback early** - Don't write PRD in isolation
   - Share draft with eng/design/stakeholders
   - Iterate based on feedback
   - Get sign-off before implementation starts

6. **Keep it updated** - PRD is living document
   - Update when requirements change
   - Update when decisions are made
   - Update when launched (add "Actual Results" section)

7. **Use with AI Project Playbook**:
   - PRD → informs CLAUDE.md (tech stack, architecture)
   - PRD → informs feature breakdown (user stories → tasks)
   - PRD → informs validation (success metrics → tests)

**This PRD ensures:**
- ✅ Everyone aligned on what we're building and why
- ✅ Clear success metrics (not "we'll know it when we see it")
- ✅ Scoped appropriately (MVP → v2 → v3)
- ✅ Executable by eng team (clear requirements)

**Pro tip:** For smaller features, use a lightweight version (sections 1-5 only). For major features, use full template.

---

**🎯 Remember: A good PRD answers "What and Why". The implementation plan answers "How and When".**

**Write PRDs that your future self (6 months from now) will understand. 🚀**
