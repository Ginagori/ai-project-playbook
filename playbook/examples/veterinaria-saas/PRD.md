# Product Requirements Document - VetCare SaaS

**Multi-tenant platform for veterinary clinics**

---

## Executive Summary

VetCare is a SaaS platform that helps veterinary clinics manage appointments, medical records, and client communication. Designed for clinics with 1-10 veterinarians and 50-500 active pets.

**Target Market:** Small to medium veterinary clinics in Latin America
**Business Model:** Subscription SaaS ($49-199/month per clinic)
**Timeline:** 8-12 weeks MVP

---

## Mission

Enable veterinary clinics to focus on animal care by automating administrative tasks and providing easy access to medical histories.

---

## MVP Scope

### In Scope (MVP)
1. **Pet Management**
   - CRUD pets (name, species, breed, age, owner)
   - Upload pet photos
   - View medical history

2. **Appointment Scheduling**
   - Create/edit/cancel appointments
   - Calendar view (day/week/month)
   - Automatic email reminders (24h before)
   - Conflict detection (double-booking prevention)

3. **Medical Records**
   - Create medical record after appointment
   - Diagnosis + treatment + prescriptions
   - Attach files (X-rays, lab results)
   - View chronological history per pet

4. **Multi-Tenancy**
   - Clinic signup (self-service)
   - User roles: Admin, Vet, Receptionist
   - Complete data isolation (RLS)

5. **Billing (Basic)**
   - Record services rendered
   - Generate simple invoice
   - Export to PDF

### Out of Scope (Future)
- ❌ Online payments
- ❌ Inventory management (medications)
- ❌ SMS notifications
- ❌ Telemedicine
- ❌ Mobile app

---

## User Stories

### Clinic Owner
1. As clinic owner, I want to sign up and create my clinic account in <5 minutes
2. As clinic owner, I want to add my veterinarians and staff with appropriate permissions
3. As clinic owner, I want to see usage analytics (# appointments, revenue, top clients)

### Veterinarian
1. As vet, I want to see my daily schedule at a glance
2. As vet, I want to create a medical record during/after appointment in <2 minutes
3. As vet, I want to view complete medical history of a pet before appointment
4. As vet, I want to attach lab results/X-rays to medical records

### Receptionist
1. As receptionist, I want to book appointments and avoid double-booking
2. As receptionist, I want to see which vets are available at specific times
3. As receptionist, I want to send appointment confirmations automatically
4. As receptionist, I want to check in pets when they arrive

### Pet Owner (External)
1. As pet owner, I receive email reminder 24h before appointment
2. As pet owner, I can cancel appointment via email link

---

## Architecture

### Three-Layer Architecture
- **Presentation:** FastAPI routes
- **Business:** Services (appointment logic, validation)
- **Data:** Repositories (Supabase access with RLS)

### Multi-Tenancy
- Shared database with RLS
- `clinic_id` on every table
- Postgres RLS policies enforce isolation

---

## Tech Stack

**Backend:**
- FastAPI (Python)
- Supabase (Postgres + Auth + Storage)
- SendGrid (email notifications)

**Frontend:**
- React + TypeScript
- Zustand (state)
- Tailwind + shadcn/ui

**Deployment:**
- Backend: Railway
- Frontend: Netlify
- Cost: $300-500/month

---

## Success Criteria

**Week 4:**
- [ ] 3 clinics onboarded (beta testers)
- [ ] 50+ pets registered
- [ ] 100+ appointments scheduled

**Week 12:**
- [ ] 10 paying clinics
- [ ] >80% appointment show-up rate
- [ ] <2% error rate
- [ ] <1s p95 response time

**Revenue:**
- Month 3: $500 MRR (10 clinics × $50)
- Month 6: $2,000 MRR (40 clinics)
- Month 12: $10,000 MRR (100 clinics)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data breach | CRITICAL | RLS + encryption at rest + audit logs |
| Slow adoption | HIGH | Free trial (30 days) + onboarding calls |
| Scheduling conflicts | MEDIUM | Optimistic locking + conflict detection |
| Email deliverability | MEDIUM | Use SendGrid + verify domain |

---

**Timeline:** 8-12 weeks from start to paying customers
