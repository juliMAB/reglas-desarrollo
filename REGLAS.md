# REGLAS DE DESARROLLO — v1.2

> **Estado:** aprobado. v1.2 incorpora los hallazgos de la fase 2 (contrato + productor + QA en dispositivo).
> v1.1: QA móvil, puertas N/A, entorno, entrega. v1.2: QA separado del que construye, vacío ≠ error,
> verificación desde el consumidor, host con USB como condición.
> v0.1: primeras reglas. v0.2: seis decisiones. v0.3: contratos por ecosistema, validador, registro.
> v0.4: códigos de salida, ids de mensaje, `reply_to`. v1.0: pendientes cerrados.
> v1.1: QA móvil, puertas N/A, entorno, entrega a dispositivo, precedencia.
> Objetivo final: una tool portable, en lenguaje técnico y genérico, que cualquier modelo entienda.

---

## 0. Qué es y qué no es

**Es** la capa de *cómo se construye y se entrega* software.

**No es:**
- `SCRUM-AGENTES.md` → define el *proceso* (HU, estados, roles, vueltas). Este documento lo da por sentado.
- `REGLAS-PUERTOS.md` → fuente de verdad de puertos y exposición. Este documento obliga a leerlo, no lo duplica.
- Prosa aspiracional. Cada regla tiene que poder verificarse con un comando, un archivo o una prueba.

**Lenguaje:** técnico y explícito, sin modismos. Debe entenderlo cualquier modelo, no solo los especializados en código.

---

## 1. Principios (los mandamientos)

**M1 — Un módulo, un proyecto, un repo.** Cada parte modular vive en su propio directorio y repositorio.

**M2 — Ningún módulo conoce a otro.** Conoce su contrato de entrada y su contrato de salida.

**M3 — La interfaz es el dato, no el código.** Prohibido importar código de otro módulo, leer su base de datos o abrir sus archivos internos.

**M4 — Cada módulo arranca solo.** Sin datos del productor: estado vacío o fixtures. Nunca crashea, nunca queda en blanco.

**M5 — Reemplazar un productor no toca a los consumidores.** Si los toca, el contrato estaba mal.

**M6 — El transporte es reemplazable; el contrato no.**

**M7 — Cada proyecto hace su propio QA.**
- **web/UI:** se entra, se navegan las rutas principales, se verifica respuesta y contenido.
- **script/CLI:** valores aleatorios, no se rompe, exit codes correctos.
- **servicio/API:** request real, respuesta validada contra contrato.
- **app móvil:** se instala, se lanza, se confirma la activity en foco y se saca captura.
- **librería:** tests unitarios.

Si el proyecto expone interfaz, además la URL tiene que ser accesible. Si no, no se le exige URL.
Un tipo no listado no queda sin prueba: se declara el tipo nuevo y su prueba mínima en el proyecto, y se propone para esta lista.

**M8 — Los proyectos no se hablan entre sí.** Comunicación en estrella: cada proyecto ↔ orquestador. Nunca proyecto ↔ proyecto.

**M9 — El QA no es el que construye.**
Quien prueba no es quien programó, y no comparte su contexto. No leyó el razonamiento, no sabe qué se
intentó ni por qué. Entra con el entregable y el contrato, y lo usa como lo usaría alguien que no
sabe nada. Si el que construye también prueba, está validando su recuerdo, no el producto.

---

## 2. El contrato de datos

### 2.1 Definición
Un contrato es el acuerdo verificable sobre la forma del dato que un productor entrega y un consumidor acepta. No es código ni documentación libre: es una especificación que una máquina puede validar.

### 2.2 Dónde vive
**Un repo de contratos por ecosistema.**

```
~/proyectos/beneficios/contratos/
├── descuentos/
│   ├── v1.0.0/
│   │   ├── contrato.md       semántica: qué significa cada campo
│   │   ├── schema.json       JSON Schema (la forma, verificable por máquina)
│   │   ├── ejemplo.json      fixture oficial
│   │   └── vacio.json        respuesta cuando no hay datos
│   └── CHANGELOG.md
└── comercios/
    └── v1.0.0/...
```

Separado del productor y del consumidor. Ni el scraper ni la web son dueños del contrato.

### 2.3 Versionado
**Semver por contrato**, independiente entre contratos.
- `patch`: campo opcional nuevo o corrección de documentación.
- `minor`: campo obligatorio nuevo con default retrocompatible.
- `major`: se quita o cambia tipo de un campo. Requiere aviso y plan de migración.

Productor y consumidor declaran qué versión usan.

### 2.4 Formato: JSON Schema
`schema.json` es la forma legible por máquina. Se eligió JSON Schema porque es estándar, explícito y conocido por cualquier modelo, sin depender de un lenguaje de programación. `contrato.md` acompaña con la semántica que el schema no expresa (qué significa cada campo en el negocio).

### 2.5 Validador
**Un validador común, en forma de CLI.**

Qué es: un programa que recibe un contrato y un archivo de datos, y responde si el dato cumple o no, indicando el campo exacto que falla.

"Forma" significa cómo se invoca. Se elige **CLI** porque:
- Cualquier IA lo corre con un comando, sin saber el lenguaje en que está hecho.
- El resultado es un código de salida (`0` válido, `1` inválido) más un informe legible.
- No obliga a los proyectos a importar una librería ni a compartir lenguaje.

```
validador validar contratos/descuentos/v1.0.0 datos.json
```

- Un solo validador para todo el ecosistema. No se reimplementa por módulo.
- El `ejemplo.json` de cada contrato debe pasar el validador. Si no pasa, el contrato está roto.

**Códigos de salida (contrato del validador con el resto del sistema):**

| Código | Significado | Qué hace el agente |
|---|---|---|
| `0` | El dato cumple el contrato | Sigue |
| `1` | El dato NO cumple | Frena y muestra el informe |
| `2` | No se pudo validar (archivo inexistente, schema inválido, error de uso) | Frena distinto: el problema es del entorno, no del dato |

Separar `1` de `2` importa: un dato mal formado es un bug del productor; un schema roto es un bug del contrato. No se confunden.

Uso típico en cualquier lenguaje o por cualquier agente:

```
validador validar contrato.json datos.json
si sale 0 -> ok; si sale 1 -> el productor mandó mal; si sale 2 -> revisar el contrato o la ruta
```

### 2.6 Vacío y error son estados distintos

| Situación | Respuesta | Significa | UI |
|---|---|---|---|
| Hay datos | `200` + lista con elementos | Normal | Muestra los datos |
| No hay datos | `200` + `[]` o `null` según contrato | El productor respondió y no hay nada | Estado vacío, **no** reintenta |
| No está | timeout, conexión rechazada, `5xx` | El productor no respondió | Estado de error, **con** reintento |
| Pedido inválido | `4xx` | El consumidor pidió mal | Error, sin reintento |

Regla: usar el mismo estado visual para "no hay datos" y "no está" es un bug. El usuario no puede
distinguir si el sistema está sano o roto, y el operador no puede diagnosticar desde la pantalla.
El contrato define `vacio` y `errores` por separado; el consumidor está obligado a renderizarlos distinto.

**El error tiene dos niveles.** Mensaje para el usuario en lenguaje natural; detalle técnico al log,
no a la pantalla. Un `IllegalStateException` visible en la UI es fuga de implementación, no información.

---

## 3. Layout de proyectos

```
~/proyectos/
├── beneficios/
│   ├── web/          consumidor
│   ├── scraper/      productor
│   └── contratos/    repo de contratos del ecosistema
├── carteras/
│   ├── tracker/
│   ├── ingesta/
│   └── contratos/
└── <ecosistema>/<modulo>/
```

Agrupar no es acoplar: cada módulo sigue siendo repo independiente.

---

## 4. Puertos y exposición

**P1** — Antes de escribir código de servidor: leer `REGLAS-PUERTOS.md` y reservar el puerto en la tabla, en el mismo commit.
**P2** — Antes de levantar: `ss -tlnp | grep :PUERTO`. Si está ocupado, no matar nada.
**P3** — Bind por defecto `127.0.0.1`. `0.0.0.0` es excepción justificada por escrito.
**P4** — Publicación con `tailscale serve` y el puerto HTTPS asignado. Nunca abrir puertos en el router.
**P5** — Si expone servicio: la URL se verifica **desde el consumidor**. Un 200 medido en el host no
prueba que el teléfono, el navegador o el cliente lleguen. La evidencia es la respuesta vista por
quien consume, no por quien sirve.

---

## 5. Puertas de calidad

**G1 — Antes de codear:** contrato identificado con versión y puerto reservado.
**G2 — Antes de levantar:** puerto verificado libre.
**G3 — QA propio (M7):** prueba ejecutada según tipo de proyecto, salida pegada.
**G4 — Antes de cerrar la HU:** evidencia en `evidencia/HU-<n>.md` (o `evidencia/<slug>.md` si no hay HU), con la salida real de G3.

### 5.1 Puertas no aplicables

Una puerta puede declararse **N/A**, pero solo con justificación escrita en la evidencia.
Formato: `G1: N/A — la app no produce ni consume datos ni escucha en un puerto`.

Sin justificación, una puerta N/A se considera **no pasada**. No existe el "la salteo porque no aplica".

---

## 6. Mensajería entre agentes y módulos

### 6.1 Topología: estrella
```
proyecto A ──┐
proyecto B ──┼── orquestador (Chopy) ── humano
proyecto C ──┘
```
- El orquestador accede a todos los buzones.
- Todos acceden al orquestador.
- **A ↔ B prohibido.**

### 6.2 Registro de agentes
Análogo a `REGLAS-PUERTOS.md`, pero para agentes: un archivo único, `REGISTRO-AGENTES.md`, en la raíz del workspace.

| Campo | Qué contiene |
|---|---|
| `nombre` | rol o id estable del agente (`product-owner`, `developer`, `ag-0001`) |
| `ses_id` | identificador de la sesión/chat |
| `path` | directorio de trabajo o buzón que usa |
| `ultimo_latido` | última vez visto, ISO-8601 UTC |
| `proyecto` | ecosistema al que pertenece |
| `estado` | activo / busy / inactivo / retirado |

Formato de línea, ya implementado en `agentes-chat`: `NOMBRE | SES_ID | PATH | ULTIMO_LATIDO`.

Reglas:
- Un agente nuevo se registra antes de mandar su primer mensaje.
- Un nombre no se reutiliza. Retirado queda en la tabla, no se borra.
- El registro es la dirección. No reemplaza al buzón: dice quién existe y dónde recibe.
- El registro es por ecosistema; el orquestador ve todos.

### 6.3 Identificadores: mensaje, ticket y cursor

Son tres cosas distintas y no se deben mezclar.

**1. `id` de mensaje (el ticket).** Único por mensaje. Formato ya en uso: `h-<hex8>`.
Se genera al crear el mensaje y no cambia nunca.

**2. `reply_to` (correlación).** Campo del mensaje que contiene el `id` del pedido que responde.
Sin este campo, una respuesta es un mensaje suelto: no se sabe a qué contesta.

**3. `since` (cursor).** Posición de lectura de cada consumidor. No identifica mensajes: indica
"ya leí hasta acá". Es estado del lector, no del mensaje.

Ejemplo:

```
{ "id": "h-3f2a1b9c", "ts": "...", "from": "developer", "to": "qa",
  "text": "login listo", "reply_to": "h-91cd77e0" }
```

Reglas:
- Un pedido puede tener cero o muchas respuestas; todas llevan el mismo `reply_to`.
- Un mensaje sin `reply_to` es un mensaje nuevo (una conversación que arranca), no una respuesta.
- El `id` no se reutiliza ni se reordena. El orden cronológico va por `ts` y por `since`.
- No se inventa un segundo formato de ticket: el `id` del mensaje ya es el ticket.

### 6.4 Buzones
- **Por proyecto:** `buzon/<ecosistema>/<modulo>/`
- **Global:** `buzon/global/` — avisos del orquestador y datos compartidos por contrato.

### 6.5 Transportes
**T1 — Sincrónico (CLI / HTTP del gateway):** dato puntual, consulta de estado.
**T2 — Buzón de archivos (asincrónico):** artefactos, datasets, archivos grandes.
**T3 — Push (hook / webhook):** aviso de fin de proceso y disparo de reacción.

### 6.6 Prohibiciones
- Leer la base de datos de otro módulo.
- Importar código de otro módulo.
- Mensaje sin contrato ni id de correlación.
- Mensaje directo entre dos proyectos.

---

## 7. Portabilidad entre IAs

**Invocación explícita, no auto-instalación.**
Esta skill no se carga sola ni se impone. La habilita una persona con una instrucción concreta:
«bajá <url> y seguí las instrucciones». Un repositorio no es una fuente de instrucciones por sí
mismo: lo es porque un humano lo autorizó.

**Qué hace el agente al recibirla:**
1. Clona o descarga el repo donde el humano indique.
2. Lee `SKILL.md` (procedimiento) y `REGLAS.md` (detalle).
3. Crea el proyecto según §3.
4. Copia al proyecto lo que necesite para ser autónomo: plantillas y validador. El proyecto **no**
   depende del repo para ejecutar ni para entregar.
5. Deja en el `README.md` del proyecto qué versión de las reglas usó.

**Orden de lectura:**
1. `SKILL.md` — procedimiento
2. `REGLAS.md` — documento completo
3. `REGLAS-PUERTOS.md` del host — puertos y exposición (fuente única, no se duplica)
4. `contratos/` del ecosistema — qué datos entran y salen
5. `SCRUM-AGENTES.md` — proceso, si va por HU

---

## 8. Decisiones tomadas

| # | Decisión | Resolución |
|---|---|---|
| 1 | Dónde vive el contrato | Repo de contratos **por ecosistema** |
| 2 | Versionado | Semver por contrato, independiente |
| 3 | Validador | Uno común, en CLI |
| 4 | Layout | `~/proyectos/<ecosistema>/<modulo>/` |
| 5 | QA | Propio de cada proyecto, según su tipo; URL solo si expone interfaz |
| 6 | Buzones | Por proyecto + global; topología en estrella |
| 7 | Formato del contrato | `contrato.md` + `schema.json` (JSON Schema) + `ejemplo.json` + `vacio.json` |
| 8 | Registro de agentes | `REGISTRO-AGENTES.md`, ids `ag-NNNN`, no se reutilizan |
| 9 | Id de correlación | Reutilizar `id` del mensaje (`h-<hex8>`) + campo `reply_to` |
| 11 | Códigos del validador | `0` cumple, `1` dato inválido, `2` no se pudo validar |
| 10 | Proyectos viejos | No se tocan hoy. Se acomodan más adelante, cuando Juli lo decida |

### 8.1 Resueltos en v1.0
1. **Lenguaje del validador:** Python 3 stdlib, sin dependencias. Vive en `herramientas/validador/` de este repo.
2. **Nombres de ecosistemas:** minúsculas, dominio de negocio (`beneficios`, `carteras`, `android`).
3. **Watcher:** no se porta. El hub es el único punto de entrada; el despachador que despierta agentes es lo último de la lista.
4. **Auth del hub:** sin token. La tailnet es el control de acceso. Bind a loopback y publicación con `tailscale serve`.

---

## 9. Reglas de convivencia con lo existente

- `REGLAS-PUERTOS.md`: única verdad de puertos. `SCRUM-AGENTES.md`: única verdad de proceso. Si hay discrepancia, gana el específico.
- Proyectos en producción (beneficios-ui, carteras, mora, portfolio) **no se reescriben**.
- Nada se implementa ni se instala hasta aprobación explícita de Juli.

---

## 10. Piloto

Primer uso real de estas reglas: app Android mínima ("hola") construida por una sesión
con contexto limpio, sin acceso a la conversación donde se escribieron las reglas.

- El entregable es el APK funcionando en el teléfono **y** un `HALLAZGOS.md` con todo lo que
  el documento no alcanzó a explicar.
- Criterio de éxito: el APK abre. Criterio de valor: la lista de hallazgos.
- Cada hallazgo se convierte en una regla nueva o en una corrección de las existentes.

---

## 11. Entorno y toolchain

**E1 — Verificar el binario, no el producto.**
"JDK instalado" no se puede verificar. `javac -version` sí. Toda afirmación sobre el entorno
nombra el comando exacto que la comprueba.

**E2 — Licencias antes de instalar.**
Las toolchains con licencia (Android SDK) se aceptan antes del primer paquete, no reaccionando al error.

**E3 — Las toolchains Java no heredan el proxy.**
Si `curl` responde 200 y `sdkmanager` (o cualquier cliente Java) falla, el problema es el cliente,
no la red. Se prueba con las variables de proxy removidas antes de diagnosticar el firewall.

**E4 — Autorización por objetivo.**
Se autoriza "dejar el toolchain Android funcional", no una lista cerrada de paquetes. Una lista
siempre queda corta y obliga a frenar por algo trivial.

**E5 — Un toolchain canónico por ecosistema.**
Si el proyecto no lo define, se elige el más portable, se documenta en `README.md` y se declara
por qué. En Android el mínimo (aapt2 + javac + d8 + zipalign + apksigner) evita AGP y Maven;
Gradle se elige por mantenibilidad, no por defecto.

**E6 — Una sola versión de cada herramienta, declarada.**
Si el host ya trae una (`/usr/bin/adb`) y el SDK trae otra, el proyecto usa una por ruta absoluta
y lo dice. No se depende del `PATH` por accidente.

**E7 — El acceso al entorno se verifica antes de empezar.**
Antes de la primera línea de código: SSH al host del dispositivo y `adb devices` con el dispositivo
en estado `device`. Si no está, se declara bloqueo y no se simula progreso. Un entorno que "debería
funcionar" no es un entorno verificado.

**E8 — Capturar en dispositivo exige pantalla encendida y desbloqueada.**
Un `screencap` con la pantalla apagada devuelve una imagen negra y **no es evidencia**. Antes de
capturar: `input keyevent KEYCODE_WAKEUP`, verificar `dumpsys power | grep mWakefulness=Awake`, y
si hay bloqueo, deslizar. Si el dispositivo se bloquea durante la sesión de QA, se documenta el
método de desbloqueo o se desactiva el bloqueo temporalmente.

---

## 12. Entrega a dispositivos

**D1 — Un servicio se entrega con URL. Un artefacto se entrega instalado.**
No hay "te paso el archivo": hay instalación y evidencia de que se ejecuta.

**D2 — El pairing inalámbrico de Android exige misma subred.**
Por Tailscale/VPN no funciona: el puerto abre y el handshake muere. Verificado con adb 34 y 37.
No se pierde tiempo intentándolo.

**D3 — El host con USB es parte del entorno, y se verifica antes de empezar.**
Si el entregable corre en un dispositivo físico, tiene que existir un host con acceso al dispositivo
y capacidad de ejecutar comandos. Sin eso el proyecto no arranca: no se "prueba después".

Verificación previa obligatoria: `ssh <host> adb devices` lista el dispositivo con estado `device`.
Si dice `offline`, `unauthorized`, o aparece solo un `emulator-*`, **no hay canal**.

Canales aceptados, en orden:
1. USB en un host con ejecución remota (SSH): `adb install`, `am start`, `screencap` desde ahí.
2. USB en otro host con el servidor adb expuesto a la tailnet: `adb -H <ip>` desde acá.
3. Instalación manual por el humano, **solo si 1 y 2 no existen**, y declarada como tal.

La entrega y el QA se hacen **desde el host del dispositivo**, no desde el host de desarrollo.

**D4 — Honestidad de la evidencia.**
Si existe canal con el dispositivo, la evidencia sale de ahí: versión instalada, activity en foco,
captura. Si no existe y el humano instala, la evidencia es su confirmación o su captura, **etiquetada
como humana**. Está prohibido presentar una confirmación humana como salida de `adb`, y también
inventar una salida que no existió. La evidencia puede ser débil; falsa nunca.

**D5 — Servicio temporal de entrega.**
Si hace falta servir un artefacto, se reserva el puerto, se bindea a la IP de la tailnet (nunca
`0.0.0.0`), se verifica el hash de lo servido y se apaga al terminar. El puerto queda RETIRADO.

**D6 — El endpoint de un consumidor es configuración, no código.**
La URL del productor se lee de configuración por entorno (dev / QA / prod). Cambiar de entorno no
requiere recompilar. Si la configuración falta, el consumidor arranca igual y muestra un error
explícito. Un APK con la URL compilada adentro ata la prueba a la topología de red del momento.

---

## 13. Precedencia de instrucciones

Cuando dos instrucciones se contradicen, gana la de arriba:

1. Seguridad, secretos y permisos.
2. Instrucción específica de la tarea en curso.
3. Estas reglas.
4. `AGENTS.md` y preferencias del workspace.

Si el conflicto es real y no trivial, se resuelve y **se anota como hallazgo**. Un conflicto
silencioso es una regla que falta.

---

## 14. Cierre del piloto (2026-10-21)

**Resultado:** APK compilado, firmado, instalado y visible en el teléfono: `hola` centrado en
pantalla. Confirmado por Juli. La verificación fue manual porque el pairing por tailnet no es viable.

**Lo que funcionó sin que se le indicara:**
- El layout por ecosistema: creó `~/proyectos/android/hola/` sin preguntar.
- Leyó el contrato de beneficios como material de forma.
- Reservó el puerto de entrega y lo dejó documentado (P1).
- No inventó evidencia: declaró el bloqueo en vez de simular una salida de `adb`.

**Lo que falló:**
- Entrega a dispositivo (H-09, H-13, H-14): el hueco más grande.
- Provisión de entorno (H-04 a H-08): supuestos del host que no se cumplían.
- Puertas sin estado N/A (H-02) y evidencia sin HU (H-03).

**Duración:** ~35 minutos de sesión limpia, sin intervención del orquestador.

**Conclusión:** el documento alcanza para construir y entregar en un contexto limpio. No alcanza
para móvil sin reglas explícitas de entrega. v1.1 corrige eso.

---

## 15. Cierre de la fase 2 (2026-10-21)

**Resultado:** contrato `mensaje` v1.0.0, productor propio en 3031 publicado en 8454, y la app
mostrando el texto del contrato. Juli lo verificó en el teléfono: "hola desde el contrato".

**Huecos que originaron v1.2:**
- M4 no distinguía vacío de productor ausente → §2.6.
- El QA lo hizo el mismo agente que construyó → M9.
- P5 validaba en el host → P5 reescrita.
- El host con USB no era parte del entorno → D3 y E7.
- Evidencia humana sin etiqueta → D4.

**Acceso:** el host con el dispositivo quedó con OpenSSH y una clave autorizada, sin contraseña. `adb` existe en
`C:\Users\JulianAguirre\AppData\Local\Android\Sdk\platform-tools`.
Pendiente: el teléfono no aparece en `adb devices` (solo `emulator-5554 offline`). Sin eso, D3
sigue sin cumplirse y el QA en dispositivo no se puede hacer.
