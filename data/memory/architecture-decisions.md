# Archie Agent — Decisiones de Arquitectura

## AD-001: Autenticacion Biometrica para Modificar Agentes
**Fecha**: 2026-02-22
**Decidido por**: Natalia
**Estado**: Aprobado (diseno por fases)

### Contexto
Solo Ivan Dario Suarez y Natalia Gomez tienen autoridad para modificar agentes. Cualquier operacion critica (modificar Core Soul, push a repos, activar/desactivar agentes, cambiar config de seguridad, acceso a datos sensibles) requiere autenticacion biometrica.

### Alcance
- Modificar Core Soul / Directiva 0
- Cualquier cambio en codigo del agente (push, merge PRs, cambios en PRPs)
- Operaciones administrativas (activar/desactivar agentes, cambiar config, admin panel)
- TODO lo critico sobre agentes

### Dispositivos
- Laptops Windows (Ivan y Natalia)
- Telefonos moviles (pueden usar huella / Face ID)

### Diseno: Clasificacion de Operaciones

| Nivel | Tipo | Accion requerida | Ejemplos |
|-------|------|-----------------|----------|
| L0 | Lectura | Automatico | Leer archivos, buscar en codebase, consultar docs |
| L1 | Escritura reversible | Informar | Crear/editar archivos locales, ejecutar tests |
| L2 | Escritura irreversible | Confirmar | Push a repo, crear/borrar branches, modificar DB |
| L3 | Critico + externo | Autenticacion fuerte | Modificar Core Soul, activar/desactivar agentes, cambiar seguridad, acceso a datos sensibles |

### Fase 1 — Archie Agent MVP (ahora)
- Clasificacion de operaciones L0-L3 implementada en el executor
- L2: Archie PAUSA y pide confirmacion interactiva (estan en terminal)
- L3: Requiere confirmacion + TOTP como segundo factor temporal
- GitHub branch protection + required reviews (requiere GitHub Pro/org)
- Audit log de todas las operaciones L2-L3

### Fase 2 — NOVA (futuro)
- WebAuthn/FIDO2 passkeys en admin panel
- Servicio de aprobaciones con push notifications al telefono
- Biometricos del telefono (huella / Face ID) como factor de autenticacion remota
- Firma criptografica de aprobaciones con audit trail
- Dashboard de aprobaciones pendientes

### Flujo Autonomo (Fase 2)
```
Archie ejecutando autonomamente
    |
    |-- L0-L1: Procede sin pedir permiso
    |
    |-- L2: PAUSA -> Confirmacion interactiva
    |
    +-- L3: PAUSA -> Notificacion push al telefono
                   -> Autenticacion biometrica (huella/Face ID)
                   -> Token firmado criptograficamente
                   -> Archie recibe token -> Procede
```

### Impacto en PRPs
- PRP 02 (Security Foundation): Agregar clasificacion de operaciones L0-L3
- PRP 08 (Kill Switch & Circuit Breakers): Integrar con nivel de autorizacion
- Futuro PRP para servicio de aprobaciones (Fase 2, cuando NOVA este listo)
