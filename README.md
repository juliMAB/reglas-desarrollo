# reglas-desarrollo — cómo se construye software en este ecosistema

**Versión:** 1.2 · **Estado:** release para un solo agente.

## Alcance de esta versión

Esta versión está pensada y probada para **un solo agente** que ejecuta todos los roles:
construye, se autoimpone las puertas y entrega evidencia. No define reparto de roles ni handoff
entre agentes; eso corresponde a una versión posterior (2.0).

Lo que sí exige: contrato, layout por ecosistema, puertos, QA propio y evidencia verificable.
El control de la evidencia queda del lado humano, porque el agente que construye es el mismo que
la produce.

Este repo es la fuente única de las reglas de desarrollo: arquitectura modular por contrato,
puertos y exposición, QA, entrega a dispositivos y precedencia de instrucciones.

Se aplica a todo proyecto de software. No aplica a charlas, consultas ni tareas de una sola línea.

## Cómo se usa

La habilita una persona, con una frase:

> «Bajate esta skill: <url>. Seguí las instrucciones y desarrollá <proyecto>».

Sin esa instrucción, este repo es solo documentación. No se auto-instala, no se auto-carga y no
tiene prioridad sobre nada. La autoridad la da el humano que lo invoca.

Una vez invocado, el agente:

1. Lee `SKILL.md` y `REGLAS.md`.
2. Crea el proyecto según el layout de §3.
3. Copia al proyecto lo que necesita para ser autónomo: plantillas y validador.
4. Deja anotado en el `README.md` del proyecto qué versión de reglas usó.

## Estructura

```
SKILL.md                  procedimiento para el agente
REGLAS.md                 documento completo (v1.2)
plantillas/contrato/      schema.json + contrato.md + ejemplo.json + vacio.json
plantillas/evidencia/     plantilla de evidencia por HU
plantillas/AGENTS.md      opcional: contexto propio del proyecto
herramientas/validador/   validador CLI (Python 3 stdlib, sin dependencias)
ejemplos/android-hola/    caso real: app Android + contrato + QA
CHANGELOG.md              qué cambió y por qué
```

## Cómo lo consume cada herramienta

No hay integración automática. El mismo paquete funciona en cualquier agente porque es texto:

| Herramienta | Cómo se invoca |
|---|---|
| OpenClaw | «bajá <url> y seguí las instrucciones» |
| opencode | ídem |
| Claude Code | ídem |
| DeepSeek Harness | ídem |
| Cualquier modelo | ídem; `REGLAS.md` es markdown plano |

`plantillas/AGENTS.md` es opcional y sirve para el contexto **del proyecto** (qué módulo es, qué
contrato usa). No es el mecanismo por el que se cargan las reglas.

## Regla de oro

Cada regla tiene que poder verificarse con un comando, un archivo o una prueba. Si no se puede
verificar, no es regla: es deseo.
