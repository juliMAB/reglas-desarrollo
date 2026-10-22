---
name: reglas-desarrollo
description: Reglas para construir y entregar software en este ecosistema. Usar antes de crear, modificar o entregar cualquier proyecto de código. Cubre arquitectura modular por contrato, puertos, QA, entrega a dispositivos y precedencia.
---

# Reglas de desarrollo

Antes de escribir código, leé `REGLAS.md` completo. Este archivo es el índice operativo; el detalle está allá.

## Checklist obligatoria

**Antes de codear (G1)**
- Contrato identificado y versión declarada. Si no aplica: `G1: N/A — <justificación>`.
- Puerto reservado en `REGLAS-PUERTOS.md`, en el mismo commit. Si no aplica: N/A justificado.

**Antes de levantar (G2)**
- `ss -tlnp | grep :PUERTO` sin conflicto. Si está ocupado, no matar nada.

**Antes de decir terminado (G3)**
- Prueba propia según el tipo: web, script, API, app móvil, librería.
- Con el productor apagado, el consumidor arranca y muestra estado explícito. Nunca blanco ni cuelgue.
- Si expone servicio: la URL se verifica **desde el consumidor**, no desde el host.

**Antes de cerrar (G4)**
- Evidencia en `evidencia/HU-<n>.md` o `evidencia/<slug>.md`, con la salida real de los comandos.

## No negociable

- Un módulo, un repo. Un módulo no importa ni lee a otro: solo su contrato.
- El QA no es quien construye (M9). Contexto limpio, sin saber qué se intentó.
- Vacío ≠ error. `200 + []` no es lo mismo que timeout o `5xx`.
- El endpoint de un consumidor es configuración, no código (D6).
- Si no hay canal con el dispositivo, el proyecto no está terminado (D3/E7).
- Evidencia débil es aceptable; evidencia falsa no (D4).

## Herramientas de este repo

```
herramientas/validador/validador.py     valida datos contra un contrato JSON Schema
plantillas/contrato/                    esqueleto de contrato
plantillas/evidencia/                   esqueleto de evidencia
```

## Precedencia

1. Seguridad y permisos.
2. Instrucción específica de la tarea.
3. Estas reglas.
4. `AGENTS.md` y preferencias del workspace.

Un conflicto real se resuelve y se anota. Un conflicto silencioso es una regla que falta.
