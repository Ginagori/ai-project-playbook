# 🚀 First Project Prompts - Copy-Paste Ready

**Prompts optimizados para iniciar proyectos usando el AI Project Playbook**

---

## 🎯 ¿Cuándo Usar Este Archivo?

Usa estos prompts cuando:
- ✅ Inicias un proyecto NUEVO desde cero
- ✅ Quieres migrar un prototipo (Lovable/v0) a producción
- ✅ Necesitas configurar un proyecto de analítica de datos
- ✅ Quieres que Claude actúe como tu Project Manager

**Simplemente copia el prompt apropiado y pégalo en Claude Code.**

---

## 📋 Opción 1: Proyecto Nuevo (Guiado por PM)

**Use case:** Quiero crear un proyecto desde cero pero necesito ayuda para decidir todo.

**Prompt:**

```
Hola Claude, voy a iniciar un proyecto nuevo.

Ayúdame siguiendo el AI Project Playbook en la carpeta ai-project-playbook/:

1. Lee el Playbook para entender el sistema
2. Actúa como mi Project Manager y hazme preguntas sobre mi proyecto:
   - ¿Qué problema resuelve?
   - ¿Para quién es?
   - ¿Qué tech stack necesito?
   - ¿Qué escala espero?
3. Basado en mis respuestas, propón un tech stack apropiado
4. Crea mi CLAUDE.md completo con las 6 secciones
5. Configura la estructura inicial del proyecto

Guíame paso a paso. Haz UNA pregunta a la vez, espera mi respuesta antes de continuar.

Soy [principiante/intermedio/avanzado] en programación, ajusta tus explicaciones a mi nivel.
```

**Qué esperar:**
- Claude te hará 5 preguntas Discovery
- Propondrá tech stack con rationale
- Creará CLAUDE.md customizado
- Configurará estructura del proyecto
- Te guiará al primer PIV Loop

**Tiempo:** 30-60 minutos

---

## 🎨 Opción 2: Migrar Prototipo de Lovable/v0

**Use case:** Tengo un prototipo funcional de Lovable.dev o v0.dev que quiero llevar a producción.

**Prompt:**

```
Hola Claude, tengo un prototipo creado con [Lovable/v0] que necesito migrar a producción.

Usa la guía completa de migración del AI Project Playbook:
- Ruta de la guía: ai-project-playbook/06-advanced/lovable-to-production.md

Contexto de mi proyecto:
- **Problema que resuelve:** [describe brevemente]
- **Tech stack del prototipo:** [ej: React + Supabase + Tailwind]
- **Usuarios esperados:** [ej: 100-1000 usuarios]
- **Requisitos especiales:** [ej: multi-tenancy, payments, etc.]

Proceso que quiero seguir:
1. PHASE 1: Audit & Extract (analizar prototipo exportado)
2. PHASE 2: Design System (extraer componentes a shadcn/ui)
3. PHASE 3: Backend Reconstruction (crear backend production-ready)
4. PHASE 4: Deployment (configurar deployment escalable)

Mi prototipo exportado está en: [ruta al código exportado]

Empieza por PHASE 1. Analiza el código y crea el inventory de componentes.
```

**Qué esperar:**
- Análisis completo del prototipo
- Inventory de componentes/páginas/data models
- Gap analysis (qué falta vs. producción)
- Migración guiada fase por fase
- Sistema production-ready al final

**Tiempo:** 1-2 semanas (working incrementalmente)

---

## 📊 Opción 3: Proyecto de Analítica de Datos

**Use case:** Tengo datos limpios y quiero crear un proyecto de análisis/visualización.

**Prompt:**

```
Hola Claude, voy a crear un proyecto de analítica de datos.

Contexto:
- **Datos:** [describe el dataset - ej: "CSV con 100k filas de ventas"]
- **Objetivo:** [ej: "Dashboard interactivo de KPIs", "Análisis predictivo", etc.]
- **Usuarios:** [ej: "Solo yo", "Mi equipo de 5 personas", etc.]
- **Output deseado:** [ej: "Notebook con análisis", "Dashboard web", "API de predicciones"]

Crea mi proyecto siguiendo el AI Project Playbook:

1. Propón tech stack apropiado para analítica:
   - Python (Pandas/Polars/DuckDB)
   - Notebook (Jupyter/Marimo)
   - Visualización (Streamlit/Plotly/etc.)
   - Testing (Great Expectations para data validation)

2. Crea CLAUDE.md customizado para analítica con:
   - Core Principles enfocados en data quality
   - Testing que incluya data validation
   - Common Patterns para pipelines de datos

3. Configura estructura del proyecto:
   - Directorios para notebooks, scripts, data, tests
   - Configuración de environment (UV)
   - Data validation setup

Empieza por preguntarme detalles específicos sobre mis datos y objetivos.
```

**Qué esperar:**
- Tech stack optimizado para analítica
- CLAUDE.md con patterns de data science
- Setup de data validation (Great Expectations)
- Estructura para notebooks + scripts
- Testing apropiado para pipelines de datos

**Tiempo:** 2-4 horas setup inicial

---

## 🔧 Opción 4: Ya Tengo Código (Retrofit AI Project Playbook)

**Use case:** Tengo un proyecto existente y quiero aplicar el sistema PIV Loop.

**Prompt:**

```
Hola Claude, tengo un proyecto existente y quiero aplicar el AI Project Playbook.

Mi proyecto actual:
- **Ubicación:** [ruta al código]
- **Tech stack:** [ej: "FastAPI + React + PostgreSQL"]
- **Estado:** [ej: "MVP funcional", "En desarrollo", "Legacy code"]
- **Pain points:** [ej: "Sin tests", "Sin documentación", "Hard to maintain"]

Tareas:

1. **Analiza mi código actual:**
   - Lee la estructura del proyecto
   - Identifica patterns existentes
   - Detecta gaps de calidad (tests, types, docs)

2. **Crea CLAUDE.md basado en lo que encuentres:**
   - Extrae tech stack y versiones
   - Documenta patterns que YA estoy usando
   - Define Core Principles para estandarizar
   - Agrega testing patterns que faltan

3. **Propón plan de mejora:**
   - ¿Qué agregar primero? (tests, types, docs)
   - ¿Cómo aplicar PIV Loop a features nuevas?
   - ¿Cómo refactorizar legacy code gradualmente?

Empieza por analizar mi código en: [ruta]
```

**Qué esperar:**
- Análisis de código existente
- CLAUDE.md basado en lo que ya tienes
- Plan de mejora incremental
- Guidance para aplicar PIV Loop forward

**Tiempo:** 3-5 horas para análisis + CLAUDE.md

---

## 🤖 Opción 5: Usar /start-project Command (Si Está Configurado)

**Use case:** Ya configuraste el slash command `/start-project` y quieres usarlo.

**Prompt:**

```
/start-project
```

**Qué esperar:**
- Claude actúa como PM conversacional
- Te hace 5 preguntas Discovery
- Propone tech stack
- Crea CLAUDE.md
- Configura proyecto
- Te lleva al primer PIV Loop

**Nota:** Requiere que `.claude/commands/start-project.md` exista en tu repo.

---

## 🎯 Opción 6: Quick Start (Solo CLAUDE.md, Sin Setup)

**Use case:** Solo quiero el CLAUDE.md rápidamente, yo crearé el proyecto después.

**Prompt:**

```
Crea un CLAUDE.md para mi proyecto usando el template del AI Project Playbook.

Proyecto:
- **Nombre:** [nombre del proyecto]
- **Descripción:** [1-2 frases del problema que resuelve]
- **Tech Stack:**
  - Backend: [ej: FastAPI + Python 3.13]
  - Frontend: [ej: React + TypeScript + Vite]
  - Database: [ej: PostgreSQL]
  - Deployment: [ej: Railway + Vercel]

Usa el template en: ai-project-playbook/templates/CLAUDE.md.template

Rellena TODAS las secciones:
1. Core Principles (non-negotiable rules)
2. Tech Stack (con versiones específicas)
3. Architecture (patrón: Vertical Slice / Clean / MVC)
4. Code Style (naming, estructura, documentación)
5. Testing (frameworks, patterns, coverage target)
6. Common Patterns (API endpoints, data fetching, error handling, logging)

Customiza según mi tech stack. Hazlo conciso pero completo (200-300 líneas).

Guarda en: ./CLAUDE.md
```

**Qué esperar:**
- CLAUDE.md completo en 5-10 minutos
- Customizado a tu tech stack
- Listo para usar en próximos prompts

**Tiempo:** 5-10 minutos

---

## 💡 Tips para Mejores Resultados

### 1. Sé Específico

❌ **Vago:**
```
"Ayúdame a crear un proyecto web"
```

✅ **Específico:**
```
"Ayúdame a crear un SaaS de gestión de inventario para tiendas online.
Tech stack: FastAPI + React + PostgreSQL.
Usuarios esperados: 100-1000.
Requisitos: Multi-tenancy, RBAC, API rate limiting."
```

**Más específico = mejor propuesta de tech stack.**

---

### 2. Indica Tu Nivel de Experiencia

Incluye en tu prompt:
- "Soy principiante" → Claude explica en términos simples
- "Soy avanzado" → Claude usa términos técnicos, menos explicativo

**Ejemplo:**
```
Soy principiante en backend pero intermedio en frontend.
Explica conceptos de backend en detalle, pero puedes asumir que conozco React.
```

---

### 3. Menciona Constraints

Si tienes limitaciones, díselas:
- "Presupuesto limitado" → Claude sugerirá opciones free-tier
- "Deployment en servidor propio" → No sugerirá Vercel/Railway
- "Equipo sin experiencia en Docker" → Simplificará deployment

**Ejemplo:**
```
Constraints:
- Budget: $0-10/mes
- Deployment: Debe ser en servidor VPS que ya tengo
- Team: Solo yo, sin experiencia en DevOps
```

---

### 4. Usa el Playbook Progresivamente

**No intentes implementar TODO el Playbook en día 1.**

**Día 1:** CLAUDE.md + estructura básica
**Semana 1:** Primer PIV Loop, validation básica (Level 1-3)
**Semana 2:** Validation completa (Level 1-5), slash commands
**Mes 1:** Reference guides, templates reutilizables

**Build iterativamente.**

---

## 🚨 Errores Comunes a Evitar

### 1. No Leer el CLAUDE.md Después de Crearlo

❌ **Error:**
```
[Claude crea CLAUDE.md]
Usuario: "Ok, ahora crea un endpoint de login"
[Claude crea código sin leer CLAUDE.md]
```

✅ **Correcto:**
```
[Claude crea CLAUDE.md]
Usuario: "Lee el CLAUDE.md que acabas de crear y luego crea un endpoint de login siguiendo esas reglas"
```

**Siempre pide explícitamente que LEA el CLAUDE.md.**

---

### 2. Saltarse Discovery

❌ **Error:**
```
"Crea un proyecto de [X] inmediatamente"
[Claude crea proyecto genérico]
```

✅ **Correcto:**
```
"Guíame en Discovery para proyecto de [X]"
[Claude hace preguntas]
[Usuario responde]
[Claude propone tech stack específico a necesidades]
```

**10 minutos de Discovery ahorran semanas de refactors.**

---

### 3. No Especificar Dónde Está el Playbook

❌ **Error:**
```
"Usa el AI Project Playbook"
[Claude no sabe dónde está]
```

✅ **Correcto:**
```
"Usa el AI Project Playbook en la carpeta ai-project-playbook/
Específicamente lee: ai-project-playbook/README.md para empezar"
```

---

## 📚 Siguientes Pasos Después del Prompt

**Después de usar cualquiera de estos prompts:**

### 1. Valida el CLAUDE.md
- Lee el CLAUDE.md generado
- Ajusta si algo no te gusta
- Asegúrate de que refleje TUS preferencias

### 2. Ejecuta Primer PIV Loop
- Lee: `ai-project-playbook/00-overview/quick-start.md`
- Implementa feature simple (health check, login básico)
- Ejecuta validation completa

### 3. Itera el Sistema
- ¿Algo falló en validation? → Actualiza CLAUDE.md
- ¿Descubriste un pattern repetible? → Agrégalo a CLAUDE.md
- ¿Hay comando que repites? → Créalo como slash command

---

## ✅ Checklist Rápida

Antes de usar estos prompts, verifica:

- [ ] Tienes el AI Project Playbook en tu proyecto (carpeta `ai-project-playbook/`)
- [ ] Sabes qué problema resuelve tu proyecto (al menos vagamente)
- [ ] Decidiste qué opción usar (nuevo / migración / analítica / retrofit)
- [ ] Abriste Claude Code en la raíz del proyecto

**Si todos marcados → copy-paste el prompt apropiado y GO! 🚀**

---

## 🔗 Referencias

**Playbook Files:**
- `README.md` - Overview completo
- `00-overview/quick-start.md` - Tu primer PIV Loop en 15 min
- `01-discovery/README.md` - Proceso Discovery detallado
- `02-planning/claude-md-creation.md` - Guía completa de CLAUDE.md
- `06-advanced/lovable-to-production.md` - Migración de prototipos
- `templates/CLAUDE.md.template` - Template de CLAUDE.md

**Slash Commands (si configurados):**
- `/start-project` - PM conversacional
- `/plan-feature` - Planificar nueva feature
- `/validate` - Ejecutar validation pyramid
- `/code-review` - Review automático

---

**🎯 Remember: El mejor momento para empezar fue hace 6 meses. El segundo mejor momento es AHORA.**

**Elige un prompt, cópialo, pégalo, y empieza. El sistema se irá refinando con el uso. 🚀**
