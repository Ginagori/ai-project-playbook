# Implementación Paralela: Git Worktrees y Estrategias de Paralelización

> **Fuente:** Módulo 12 del Agentic Coding Course
> **Aplicable a:** Proyectos con múltiples features a implementar simultáneamente

---

## 💡 La Idea Central

**Este módulo va más allá de la paralelización con subagents para cubrir workflows de implementación paralela - correr múltiples agentes de coding simultáneamente en el mismo codebase usando git worktrees.**

La progresión:
```
Single agent → Subagents (research) → Worktrees (implementation) → Cloud agents (unlimited scale)
```

---

## Estrategias de Paralelización

Hay 4 patrones principales para paralelizar trabajo con AI:

| Patrón | Complejidad | Aislamiento | Ganancia de Velocidad | Caso de Uso |
|--------|-------------|-------------|----------------------|-------------|
| **Subagents** | Baja | Solo contexto | 2-5x | Research, análisis |
| **Múltiples terminales** | Baja | Ninguno | 2x | Tareas paralelas rápidas |
| **Git worktrees** | Media | Completo | 2-10x | Implementación de features |
| **Containers/Cloud** | Alta | Completo | Ilimitado | Trabajo paralelo a gran escala |

---

## Qué es Fácil vs Difícil de Paralelizar

### ✅ Fácil de Paralelizar

- Context gathering e investigación
- Web scraping y búsquedas
- Análisis de competidores/viabilidad
- Exploración de código multi-fuente

### ⚠️ Más Difícil (pero posible)

- Trabajo de implementación - agentes escribiendo código simultáneamente
- Requiere arquitectura apropiada (vertical slice) para minimizar conflictos
- Cuanto más capaces se vuelven los agentes, más importante es esto

---

## Qué Habilita la Implementación Paralela

**Vertical Slice Architecture** es la clave. Permite implementación paralela aislando features en módulos independientes:

```
project/
├── app/
│   ├── agent/          # Agent configuration
│   ├── core/           # Shared infrastructure
│   ├── features/       # Vertical slices (tools/endpoints)
│   │   ├── tool_a/     # Agent 1 trabaja aquí
│   │   ├── tool_b/     # Agent 2 trabaja aquí
│   │   └── tool_c/     # Agent 3 trabaja aquí
│   └── shared/         # Shared utilities
```

**Por qué funciona:**
- Cada feature está aislada en su propio directorio
- Agentes raramente tocan los mismos archivos
- Conflictos de merge son menores (usualmente solo registros en `main.py`)
- Patrones establecidos en una feature guían a todas las demás

---

## Git Worktrees: El Workflow

### Concepto

Un **git worktree** es un directorio de trabajo aislado que comparte el mismo repositorio git. Cada worktree puede estar en una branch diferente, permitiendo trabajo paralelo real.

```
my-project/                 # Main worktree (branch: main)
├── .git/
├── app/
└── worktrees/
    ├── feature-search/     # Worktree 1 (branch: feature/search)
    │   └── app/
    └── feature-export/     # Worktree 2 (branch: feature/export)
        └── app/
```

### El Flujo

1. **Crear worktrees** para cada feature
2. **Abrir Claude Code** en cada worktree (terminales separadas)
3. **Ejecutar `/execute`** en cada worktree con su plan respectivo
4. **Ambos completan** en ~30min vs ~1hora secuencialmente
5. **Merge** el trabajo completado de vuelta

---

## Comandos para Worktrees

### Crear Worktrees: `/new-worktree`

**Uso:**
```
/new-worktree feature-search
/new-worktree feature-search feature-export  # Paralelo
```

**Pasos (single worktree):**

```bash
# 1. Crear worktree
git worktree add worktrees/feature-search -b feature/search

# 2. Navegar
cd worktrees/feature-search

# 3. Sync dependencies
uv sync  # o npm install, etc.

# 4. Verificar con health check
uv run uvicorn app.main:app --host 0.0.0.0 --port 8124 &
sleep 3
curl -f http://localhost:8124/health
kill $SERVER_PID

# 5. Listo para desarrollo
```

**Pasos (parallel worktrees):**

Spawn 2 agentes simultáneamente:
- Agent 1: Setup worktree en puerto 8124
- Agent 2: Setup worktree en puerto 8125

### Merge Worktrees: `/merge-worktrees`

**Uso:**
```
/merge-worktrees feature-search feature-export
```

**Pasos:**

1. **Verificar precondiciones**
   - Ambas branches existen
   - No estamos dentro de un worktree

2. **Crear branch de integración**
   ```bash
   git checkout -b integration-feature-search-feature-export
   ```

3. **Merge primera feature**
   ```bash
   git merge feature-search --no-ff -m "merge: integrate feature-search"
   ```

4. **Correr tests después del primer merge**
   ```bash
   uv run pytest -v
   ```

5. **Merge segunda feature**
   ```bash
   git merge feature-export --no-ff -m "merge: integrate feature-export"
   ```

6. **Correr validation suite completa**
   ```bash
   uv run pytest -v
   uv run mypy app/
   uv run pyright app/
   ```

7. **Merge a branch original**
   ```bash
   git checkout main
   git merge integration-feature-search-feature-export --no-ff
   ```

8. **Cleanup**
   - Preguntar al usuario si quiere eliminar worktrees
   - Si sí: `git worktree remove` y `git branch -d`

---

## Best Practices

### 1. Mantén Commits Separados

Commits separados permiten review fácil (por humanos Y agentes).

### 2. Testea Features en Aislamiento

Antes de merge, verifica que cada feature funciona independientemente.

### 3. Trust but Verify

Confía en validation, pero verifica manualmente para paths críticos.

### 4. Bug Fixes vs Features

| Tipo | Estrategia |
|------|------------|
| Bug fixes pequeños | Misma branch está bien |
| Features grandes | Necesitan worktrees separados |

### 5. Escalabilidad

Con patrones apropiados establecidos (buena primera feature, standards documentados, vertical slices), podrías teóricamente correr 10+ implementaciones paralelas.

---

## Soluciones de Coding Remoto

Hay herramientas cloud-based que ofrecen ejecución paralela out-of-the-box:

| Herramienta | Descripción |
|-------------|-------------|
| **Google Jules** | `jules.google.com`, conecta a repos de GitHub |
| **OpenAI Codex** | Ejecución de agentes cloud-based similar |
| **Claude Code Web** | Claude Code remoto con environments configurables |
| **Cursor Agent Mode** | Interface agent-first de Cursor 2 |
| **Archon** | Open source con work orders de agentes |

### Cómo Funcionan

1. Conectar a tu repositorio GitHub
2. Enviar task/prompt
3. Tool spins up environment aislado
4. Agente clona repo, hace trabajo
5. Crea PR con cambios

### Limitación Actual

Estas herramientas **no usan TUS comandos custom**, system prompts, o workflows. Usan sus patrones default, no tus `/plan`, `/execute`, `/code-review` cuidadosamente diseñados.

### El Futuro

Más control sobre workflows de agentes remotos está llegando. El objetivo es mirar TU environment exacto - comandos, MCP servers, patrones - en el contexto de ejecución remota.

---

## Comparación de Estrategias

| Approach | Setup | Aislamiento | Velocidad | Caso de Uso |
|----------|-------|-------------|-----------|-------------|
| **Subagents** | Bajo | Solo contexto | 2-5x | Research, análisis |
| **Múltiples terminales** | Bajo | Ninguno | 2x | Tareas rápidas |
| **Git worktrees** | Medio | Completo | 2-10x | Implementación de features |
| **Containers/Cloud** | Alto | Completo | Ilimitado | Trabajo a gran escala |

---

## Lo que Desbloquea el Poder Paralelo Real

1. **Buenos patrones primero** - Construye una feature realmente bien
2. **Documenta todo** - Typing, logging, testing standards
3. **Vertical slice architecture** - Features no se pisan unas a otras
4. **Planes reutilizables** - Agentes siguen patrones establecidos
5. **Automatización de validation** - Trust but verify at scale

---

## Ejemplo Real: Implementación Paralela

### Escenario

Necesitas implementar 2 features: `manage-notes` y `manage-folders`

### Sin Paralelización

```
/execute manage-notes-plan.md → 30 min
/execute manage-folders-plan.md → 30 min
Total: 1 hora
```

### Con Git Worktrees

```
Terminal 1:                    Terminal 2:
cd worktrees/manage-notes      cd worktrees/manage-folders
claude                         claude
/execute plan.md               /execute plan.md
   ↓                              ↓
  30 min                        30 min
   ↓                              ↓
      Ambos terminan juntos
             ↓
      /merge-worktrees
             ↓
         Total: 30 min + merge time
```

**Ganancia: 2x más rápido**

Con más features y mejores patrones, la ganancia escala.

---

## La Dirección de la Industria

> "El IDE será, si no reemplazado, al menos muy diferente. La AI escribirá más y más de nuestro código, y nosotros haremos ingeniería de los sistemas, patrones, y workflows que queremos que la AI siga."

**Evidencia:**
- Cursor 2 pone agent mode ANTES del editor
- Todos los major providers (Google, OpenAI, Anthropic) construyen ejecución remota de agentes
- Tools open source (Archon) habilitando workflows custom en ejecución paralela

---

## Resumen

| Módulo | Foco | Paralelización |
|--------|------|----------------|
| **11 - Subagents** | Research paralelo | Context isolation |
| **12 - Worktrees** | Implementation paralela | Code isolation |

**El futuro es hacer ingeniería de workflows y patrones, no escribir cada línea de código tú mismo.**
