# Contrato: beneficios.descuentos v1.0.0

**Qué es:** la lista de descuentos que consume la web de beneficios.
**Quién lo produce:** el pipeline de beneficios (hoy vía `opencode-dashboard`).
**Quién lo consume:** `beneficios-ui`.
**Transporte:** `GET /api/beneficios` → JSON.

---

## 1. Forma

Un **array** de objetos. Un array vacío es una respuesta válida: significa "no hay descuentos", no un error.

Archivos de esta versión:
- `schema.json` — la forma, verificable por máquina.
- `ejemplo.json` — fixture oficial. Es también el requisito mínimo para el modo sin datos.
- `vacio.json` — `[]`.

## 2. Campos obligatorios

| Campo | Tipo | Semántica |
|---|---|---|
| `id` | string | Identificador estable, formato `<fuente>:<slug>`. No cambia entre actualizaciones. |
| `fuente` | string | Origen del dato: `modo`, `descuentito`, etc. |
| `titulo` | string | Título corto, es lo que se muestra como encabezado. |
| `tipo_descuento` | string | Naturaleza del descuento. Hoy solo se observó `porcentaje`. |
| `vigencia_desde` | date-time | Inicio de vigencia, ISO-8601 UTC. |
| `vigencia_hasta` | date-time | Fin de vigencia, ISO-8601 UTC. |
| `vigente` | boolean | **Lo calcula el productor.** El consumidor lo muestra, no lo recalcula. |

## 3. Campos opcionales relevantes

| Campo | Tipo | Notas |
|---|---|---|
| `porcentaje` | string \| null | String decimal (`"100"`), no number. |
| `tope`, `tope_moneda` | string \| null | Tope de reintegro y su moneda. |
| `tope_periodo` | string \| null | Observados: `month`, `day`, `campaign`, `week`. |
| `medio_pago`, `banco`, `membresia` | string \| null | Filtros de elegibilidad. |
| `requisitos` | array \| null | Lista de condiciones legibles. |
| `condiciones` | array \| null | Condiciones estructuradas, más detalladas que `requisitos`. |
| `canales` | string \| null | Texto libre. Observado: `presencial`. **No es array.** |
| `dias_validez` | string \| null | Texto libre. **No es array.** |
| `nuevoClienteDias` | integer \| null | Antigüedad mínima de cliente en días, si aplica. |
| `image_url` | string \| null | Si falta, la UI usa su placeholder. |
| `descripcion_texto` | string \| null | Texto largo original del proveedor. |

**Campos extra:** el contrato permite campos adicionales (`additionalProperties: true`). El consumidor **ignora** lo que no conoce. Un productor puede agregar campos sin subir versión.

**Campos que hoy llegan siempre en null:** `tope_cantidad`, `tope_unidad`, `tope_reintegro`, `tope_reintegro_texto`, `membresia`, `ia_extract`. El contrato los acepta null y también un valor, porque el productor todavía no los usa. Si empieza a usarlos, no es cambio de contrato.

## 4. Casos vacío y error

- **Sin datos:** `[]`. La UI muestra estado vacío. No es error, no se reintenta.
- **Productor caído:** error HTTP. La UI muestra su estado de error, no inventa datos.
- **Campo obligatorio faltante:** dato inválido. Se reporta como falla del productor, no del consumidor.

## 5. Frecuencia

El productor actualiza a diario. Se considera **viejo** un dato con más de 72 horas sin actualizar (`actualizado_en`).

## 6. Compatibilidad

- **patch:** campo opcional nuevo, documentación.
- **minor:** campo obligatorio nuevo con default retrocompatible.
- **major:** quitar campo, cambiar tipo, o cambiar el tipo de `id`. Requiere aviso y migración del consumidor.

Hoy `tipo_descuento` solo tiene el valor `porcentaje`. Aceptar un segundo valor es **minor** (el consumidor debe poder ignorarlo); cambiar el significado de `porcentaje` es **major**.

## 7. Verificación

```
validador contrato schema.json
validador validar schema.json ejemplo.json   # debe dar 0
validador validar schema.json vacio.json     # debe dar 0
```
