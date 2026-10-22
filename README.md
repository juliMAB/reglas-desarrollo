# reglas-desarrollo — cómo se construye software en este ecosistema

**Versión:** 1.2 · **Estado:** en iteración.

Este repo es la fuente única de las reglas de desarrollo: arquitectura modular por contrato,
puertos y exposición, QA, entrega a dispositivos y precedencia de instrucciones.

Se aplica a todo proyecto de software. No aplica a charlas, consultas ni tareas de una sola línea.

## Cómo usarlo

1. Leer `REGLAS.md` completo antes de escribir código. Es el contrato, no una sugerencia.
2. Copiar de `plantillas/` lo que corresponda: contrato, evidencia, `AGENTS.md` del proyecto.
3. Usar `herramientas/validador/validador.py` para validar datos contra un contrato.
4. Mirar `ejemplos/android-hola/` si hace falta un caso real de punta a punta.

## Orden de lectura

1. `REGLAS.md` — cómo se construye y se entrega.
2. `REGLAS-PUERTOS.md` del host — puertos y exposición (fuente única, no se duplica acá).
3. `contratos/` del ecosistema — qué datos entran y salen.
4. `SCRUM-AGENTES.md` — proceso, si el trabajo va por historia de usuario.
5. `AGENTS.md` del proyecto — contexto específico.

## Estructura

```
SKILL.md                  protocolo corto para agentes
REGLAS.md                 documento completo (v1.2)
plantillas/contrato/      schema.json + contrato.md + ejemplo.json + vacio.json
plantillas/evidencia/     plantilla de evidencia por HU
plantillas/AGENTS.md      stub para la raíz de cada proyecto
herramientas/validador/   validador CLI (Python 3 stdlib, sin dependencias)
ejemplos/android-hola/    caso real: app Android + contrato + QA
CHANGELOG.md              qué cambió y por qué
```

## Cómo lo consume cada herramienta

| Herramienta | Punto de entrada |
|---|---|
| OpenClaw | skill (`SKILL.md`) + `REGLAS.md` |
| opencode | `AGENTS.md` en la raíz del proyecto, apuntando acá |
| Claude Code | `AGENTS.md` o `CLAUDE.md` en la raíz del proyecto |
| DeepSeek Harness | `AGENTS.md` en la raíz del proyecto |
| Cualquier modelo | `REGLAS.md` es markdown plano |

Un `AGENTS.md` de proyecto es dos líneas: "Leé `REGLAS.md` de este repo antes de tocar código."
Sin ese archivo en el proyecto, el modelo no lee nada. Las reglas que no están en el árbol de trabajo
no existen.

## Regla de oro

Cada regla tiene que poder verificarse con un comando, un archivo o una prueba. Si no se puede
verificar, no es regla: es deseo.
