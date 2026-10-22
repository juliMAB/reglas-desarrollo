# validador

Valida datos contra un contrato JSON Schema. Sin dependencias: Python 3 stdlib.

## Uso

```
validador validar <schema.json> <datos.json> [--max-errores N] [--json]
validador contrato <schema.json> [--json]
```

## Códigos de salida

| Código | Significado |
|---|---|
| `0` | El dato cumple el contrato |
| `1` | El dato no cumple (falla del productor) |
| `2` | No se pudo validar (archivo, JSON roto, schema con keyword desconocida) |

Separar `1` de `2` evita confundir "el productor mandó basura" con "el contrato está mal escrito".

## Keywords soportadas

`type`, `properties`, `required`, `additionalProperties`, `items`, `enum`,
`minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`,
`minLength`, `maxLength`, `pattern`, `minItems`, `maxItems`, `uniqueItems`,
`format` (`date`, `date-time`, `uri`, `email`), `nullable`.

Anotaciones ignoradas: `$schema`, `$id`, `title`, `description`, `default`, `examples`.

Cualquier otra keyword **rechaza el schema con salida 2**. Es deliberado: un
`"require"` mal escrito no puede pasar desapercibido y dar por válido un dato sin
haberlo chequeado.

## Tests

```
cd ~/proyectos/herramientas/validador
python3 -m unittest discover -s tests -v
```

13 tests. Incluye un test de integración contra el contrato real de beneficios.
