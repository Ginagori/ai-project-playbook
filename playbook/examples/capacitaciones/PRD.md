# PRD - SafetyPro Training Platform

**Training management for workplace safety & health**

---

## Executive Summary

SafetyPro helps companies manage employee training for safety, health, and compliance. Built from Lovable.dev export, enhanced for production.

**Target:** SMB companies (50-500 employees) in construction, healthcare, manufacturing
**Revenue:** $99-499/month per company
**Timeline:** 6 weeks (Lovable export → production-ready)

---

## MVP Scope

### In Scope
1. **Course Management**
   - Upload training videos (Supabase Storage)
   - Upload PDFs, slides
   - Create quiz (multiple choice)
   - Set passing score (default 70%)

2. **Employee Management**
   - Bulk import employees (CSV)
   - Assign courses to employees
   - Track enrollment status

3. **Progress Tracking**
   - Video watch progress (%)
   - Quiz attempts (3 max)
   - Completion status
   - Certificate auto-generation

4. **Certificates**
   - Auto-generate PDF on course completion
   - Include: Employee name, course title, completion date
   - Download/email certificate

5. **Reporting**
   - Company dashboard: % employees trained
   - Compliance view: Who needs training
   - Export reports (CSV)

### Out of Scope (Phase 2)
- ❌ Live instructor sessions
- ❌ VR/AR training
- ❌ External compliance integrations (OSHA API)
- ❌ Mobile app

---

## User Stories

**HR Manager:**
1. Upload 10 safety courses → Assign to 200 employees → Track completion
2. View dashboard: 85% completed, 30 employees pending
3. Export compliance report for audit

**Employee:**
1. Receive email: "New training assigned: Fire Safety"
2. Watch 15-minute video → Take quiz → Pass (80%)
3. Download certificate

---

## Migration from Lovable

**Week 1-2:**
- Export code from Lovable
- Audit components (remove unused)
- Extract design system
- Setup production Supabase

**Week 3-4:**
- Implement multi-tenancy (RLS)
- Add missing features (reporting, bulk import)
- Certificate generation
- Email notifications (SendGrid)

**Week 5-6:**
- Testing with beta companies
- Bug fixes
- Deploy to Netlify
- Launch 🚀

---

## Success Criteria

**Week 6:**
- [ ] 5 beta companies onboarded
- [ ] 500+ employees trained
- [ ] 1,000+ certificates generated
- [ ] <1% error rate

**Revenue:**
- Month 3: $1,000 MRR (10 companies × $100)
- Month 12: $10,000 MRR (50 companies × $200 avg)

---

**Timeline:** 6 weeks from Lovable export to production deployment
