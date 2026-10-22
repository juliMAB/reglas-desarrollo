# HU-<n> — evidencia

> Copiar a `evidencia/HU-<n>.md` (o `evidencia/<slug>.md` si no hay HU formal).
> Sin la salida real de los comandos, este archivo no prueba nada.

**Pedido:**
**Fecha:**
**Rama / commit:**

## G1 — contrato y puerto

- Contrato: `<nombre>` v`<versión>`
- Puerto: `<número>` reservado en `REGLAS-PUERTOS.md`
- o bien: `G1: N/A — <justificación>`

## G2 — puerto libre

```
$ ss -tlnp | grep :<puerto>
<salida real>
```

## G3 — QA propio

Tipo de proyecto: web / script / API / app móvil / librería

```
$ <comando de la prueba>
<salida real>
```

- Con el productor apagado: `<qué muestra el consumidor>`
- Verificación desde el consumidor: `<URL y salida>`

## G4 — cierre

- Evidencia adjunta: capturas / logs / salida
- Veredicto: APROBADO / REABIERTO
- Si REABIERTO: qué falla y cómo se reproduce
