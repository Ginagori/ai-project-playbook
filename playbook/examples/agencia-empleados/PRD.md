# PRD - JobMatch AI

**AI-powered employment agency platform**

---

## Executive Summary

JobMatch AI helps employment agencies automate candidate-job matching using semantic search and AI scoring.

**Target:** Employment agencies (10-100 employees)
**Revenue:** $199-999/month per agency
**Timeline:** 10 weeks MVP

---

## MVP Scope

### In Scope
1. **Candidate Management**
   - Upload resumes (PDF parsing)
   - Auto-extract: name, skills, experience
   - Generate semantic embeddings
   - Search candidates by skills/experience

2. **Job Posting Management**
   - Create job postings
   - Generate job embeddings
   - Auto-match with candidates

3. **AI Matching Engine**
   - Semantic search (top 20 candidates)
   - AI scoring (Pydantic AI agent rates 0-100)
   - Explanation of match score
   - Notification to top 5 candidates

4. **Application Tracking**
   - Candidate applies to job
   - Status: pending, interviewing, offered, hired, rejected
   - Interview notes

### Out of Scope
- ❌ Client portal (companies posting jobs)
- ❌ Video interviews
- ❌ Background checks
- ❌ Payroll integration

---

## User Stories

**Recruiter:**
1. Upload 50 resumes → System parses and matches automatically
2. Post new job → See top 10 matched candidates in <5 seconds
3. Review AI match explanations to decide who to contact

**Candidate (External):**
1. Receive email: "You match 85% with Software Engineer role at TechCorp"
2. Click link to apply
3. Upload updated resume if needed

---

## Success Criteria

**Week 6:**
- [ ] 3 beta agencies onboarded
- [ ] 500+ candidates in database
- [ ] 50+ jobs posted
- [ ] 90% match accuracy (recruiter feedback)

**Revenue:**
- Month 3: $2,000 MRR (10 agencies × $200)
- Month 12: $20,000 MRR (50 agencies × $400 avg)

---

**Timeline:** 10 weeks from development to paying customers
