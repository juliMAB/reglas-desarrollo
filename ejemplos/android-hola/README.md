# Ejemplo: app Android "hola"

Caso real usado para validar estas reglas. No está copiado acá para no duplicar código;
vive en `~/proyectos/android/hola/`.

## Qué demuestra

- **Build sin Gradle:** aapt2 → javac → d8 → zip → zipalign → apksigner.
- **Contrato de datos:** `~/proyectos/android/contratos/mensaje/v1.0.0/`, campo `texto`.
- **Productor propio:** `~/proyectos/android/mensaje-api/`, puerto 3031, publicado en 8454.
- **Tres estados:** con datos, sin datos y productor caído, cada uno con UI distinta.
- **QA independiente:** sesión distinta de la que construyó, con veredicto y evidencia.
- **Entrega local por USB:** adb contra un dispositivo físico conectado al host.

## Evidencia

- `~/proyectos/android/hola/HALLAZGOS.md` — fase 1 (14 hallazgos)
- `~/proyectos/android/hola/HALLAZGOS-FASE2.md` — fase 2 (13 hallazgos)
- `~/proyectos/android/hola/evidencia/QA-fase2.md` — veredicto del QA
- `~/proyectos/android/hola/evidencia/fase2-q60/` — capturas en dispositivo

## Qué mirar primero

1. `MainActivity.java`: cómo se separa mensaje de usuario y detalle técnico.
2. `HALLAZGOS-FASE2.md`: qué huecos tenía el documento y cómo se cerraron.
3. `evidencia/QA-fase2.md`: qué significa "aprobado" con evidencia y no con relato.
