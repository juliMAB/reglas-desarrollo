# CHANGELOG — reglas de desarrollo

## 1.2 — 2026-10-21

- **M9:** el QA no es quien construye. Sesión distinta, contexto limpio.
- **§2.6:** vacío ≠ error. Cuatro estados: datos, sin datos, no está, pedido inválido.
- **§2.6:** el error tiene dos niveles. Mensaje natural en pantalla; detalle técnico al log.
- **P5:** la URL se verifica desde el consumidor, no desde el host.
- **D3:** el host con USB es parte del entorno; se verifica antes de empezar.
- **D4:** evidencia etiquetada. Humana no se presenta como `adb`.
- **D6:** el endpoint de un consumidor es configuración, no código.
- **E7:** acceso al entorno verificado antes de la primera línea de código.
- **E8:** capturar en dispositivo exige pantalla encendida y desbloqueada.

Origen: fase 2 del piloto Android (13 hallazgos).

## 1.1 — 2026-10-21

- **M7:** agregada categoría app móvil; tipos no listados se declaran con su prueba.
- **§5.1:** puertas N/A con justificación obligatoria.
- **§11:** entorno y toolchain (E1–E6).
- **§12:** entrega a dispositivos (D1–D5).
- **§13:** precedencia de instrucciones.

Origen: fase 1 del piloto Android (14 hallazgos).

## 1.0 — 2026-10-21

- Cerrados los pendientes: validador Python stdlib, nombres de ecosistema, hub sin auth.

## 0.4 — 2026-10-21

- Códigos de salida del validador (0/1/2).
- `id` de mensaje como ticket; campo `reply_to`.
- Registro de agentes alineado a `agentes-chat`.

## 0.3 — 2026-10-21

- Contratos por ecosistema, JSON Schema, validador CLI.
- Registro de agentes e id de correlación.

## 0.2 — 2026-10-21

- Seis decisiones: contrato en repo, semver por contrato, validador común,
  layout por ecosistema, QA propio, buzones por proyecto + global.

## 0.1 — 2026-10-21

- Primer borrador: mandamientos, contrato, puertos, puertas, mensajería.
