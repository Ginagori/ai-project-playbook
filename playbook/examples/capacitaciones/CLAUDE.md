# SafetyPro - Training Management SaaS

**Platform for companies to manage employee safety & health training**

---

## Core Principles

- **VERBOSE_NAMING** - Clear function and variable names
- **TYPE_SAFETY** - TypeScript strict mode
- **AI_FRIENDLY_LOGGING** - Structured logs with context
- **MULTI_TENANCY_FIRST** - company_id on all data

---

## Tech Stack

- **Frontend:** React + TypeScript (Lovable export)
- **Backend:** Supabase (Postgres + Auth + Storage + Edge Functions)
- **State:** React Query + Zustand
- **UI:** Tailwind CSS + Custom components
- **File Storage:** Supabase Storage (course materials, certificates)
- **Deployment:** Netlify (frontend) + Supabase (backend)

---

## Architecture

### Component Structure
```
src/
├── components/
│   ├── courses/
│   │   ├── CourseList.tsx
│   │   ├── CourseCard.tsx
│   │   └── CoursePlayer.tsx
│   ├── employees/
│   │   ├── EmployeeList.tsx
│   │   └── EmployeeProgress.tsx
│   └── certificates/
│       ├── CertificateGenerator.tsx
│       └── CertificatePDF.tsx
├── hooks/
│   ├── useCourses.ts
│   ├── useEmployees.ts
│   └── useProgress.ts
└── lib/
    ├── supabase.ts
    └── types.ts
```

### Multi-Tenancy
- Each company = tenant
- RLS policies isolate company data
- Subdomain routing: `acme.safetypro.app`

---

## Code Style

**Component Pattern:**
```typescript
import { useQuery } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'

interface CourseListProps {
  companyId: string
}

export function CourseList({ companyId }: CourseListProps) {
  const { data: courses, isLoading } = useQuery({
    queryKey: ['courses', companyId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('courses')
        .select('*')
        .eq('company_id', companyId)
        .order('created_at', { ascending: false })

      if (error) throw error
      return data
    }
  })

  if (isLoading) return <LoadingSpinner />

  return (
    <div className="grid gap-4">
      {courses?.map(course => (
        <CourseCard key={course.id} course={course} />
      ))}
    </div>
  )
}
```

**Supabase RLS:**
```sql
-- Ensure employees only see their company's data
CREATE POLICY company_isolation ON courses
    USING (company_id = (SELECT company_id FROM auth.users WHERE id = auth.uid()));

CREATE POLICY company_isolation ON employees
    USING (company_id = (SELECT company_id FROM auth.users WHERE id = auth.uid()));
```

---

## Database Schema

```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    industry TEXT,  -- construction, healthcare, manufacturing
    plan TEXT DEFAULT 'basic',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    department TEXT,
    position TEXT,
    hire_date DATE,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,  -- safety, health, compliance
    duration_minutes INTEGER,
    video_url TEXT,
    pdf_url TEXT,
    quiz_questions JSONB,  -- Array of questions
    passing_score INTEGER DEFAULT 70,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE course_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    employee_id UUID REFERENCES employees(id),
    course_id UUID REFERENCES courses(id),
    status TEXT DEFAULT 'not_started',  -- not_started, in_progress, completed, failed
    progress_percent INTEGER DEFAULT 0,
    quiz_score INTEGER,
    completed_at TIMESTAMPTZ,
    certificate_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_enrollments ENABLE ROW LEVEL SECURITY;

CREATE POLICY company_isolation ON employees USING (company_id::TEXT = current_setting('app.company_id', true));
CREATE POLICY company_isolation ON courses USING (company_id::TEXT = current_setting('app.company_id', true));
CREATE POLICY company_isolation ON course_enrollments USING (company_id::TEXT = current_setting('app.company_id', true));
```

---

## Common Patterns

### Pattern 1: Course Progress Tracking
```typescript
export function useCourseProgress(enrollmentId: string) {
  const updateProgress = async (progressPercent: number) => {
    const { error } = await supabase
      .from('course_enrollments')
      .update({
        progress_percent: progressPercent,
        status: progressPercent === 100 ? 'completed' : 'in_progress',
        completed_at: progressPercent === 100 ? new Date().toISOString() : null
      })
      .eq('id', enrollmentId)

    if (error) throw error

    // Generate certificate if completed
    if (progressPercent === 100) {
      await generateCertificate(enrollmentId)
    }
  }

  return { updateProgress }
}
```

### Pattern 2: Certificate Generation
```typescript
import jsPDF from 'jspdf'

export async function generateCertificate(enrollmentId: string) {
  const { data } = await supabase
    .from('course_enrollments')
    .select(`
      *,
      employee:employees(*),
      course:courses(*)
    `)
    .eq('id', enrollmentId)
    .single()

  // Generate PDF
  const pdf = new jsPDF()
  pdf.setFontSize(24)
  pdf.text('Certificate of Completion', 105, 50, { align: 'center' })
  pdf.setFontSize(16)
  pdf.text(`${data.employee.name}`, 105, 80, { align: 'center' })
  pdf.text(`has completed: ${data.course.title}`, 105, 100, { align: 'center' })

  // Upload to Supabase Storage
  const pdfBlob = pdf.output('blob')
  const fileName = `certificates/${enrollmentId}.pdf`

  await supabase.storage
    .from('certificates')
    .upload(fileName, pdfBlob)

  // Update enrollment with certificate URL
  const { data: { publicUrl } } = supabase.storage
    .from('certificates')
    .getPublicUrl(fileName)

  await supabase
    .from('course_enrollments')
    .update({ certificate_url: publicUrl })
    .eq('id', enrollmentId)
}
```

---

## Environment Variables

```bash
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=...
```

---

**Platform built for companies managing employee training and compliance.**
