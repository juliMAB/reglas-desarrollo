#!/usr/bin/env python3
"""validador — valida datos contra un contrato JSON Schema (subconjunto).

Contrato de salida:
    0  el dato cumple el contrato
    1  el dato NO cumple
    2  no se pudo validar (archivo, JSON roto, schema con keyword desconocida)

Uso:
    validador validar <schema.json> <datos.json> [--max-errores N] [--json]
    validador contrato <schema.json> [--json]

Sin dependencias: solo stdlib. Pensado para que cualquier agente lo invoque
con un comando y decida por el código de salida.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime

EXIT_OK = 0
EXIT_INVALID = 1
EXIT_ERROR = 2

# Keywords de validación soportadas.
VALIDADORES = {
    "type",
    "properties",
    "required",
    "additionalProperties",
    "items",
    "enum",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "minLength",
    "maxLength",
    "pattern",
    "minItems",
    "maxItems",
    "uniqueItems",
    "format",
    "nullable",
}

# Keywords de anotación: se aceptan, no validan nada.
ANOTACION = {"$schema", "$id", "title", "description", "default", "examples"}

FORMATOS = {"date", "date-time", "uri", "email"}


class SchemaError(Exception):
    """El schema está mal formado o usa algo no soportado."""


def _tipo_de(valor):
    if valor is None:
        return "null"
    if isinstance(valor, bool):
        return "boolean"
    if isinstance(valor, int):
        return "integer"
    if isinstance(valor, float):
        return "number"
    if isinstance(valor, str):
        return "string"
    if isinstance(valor, list):
        return "array"
    if isinstance(valor, dict):
        return "object"
    return "unknown"


def _coincide_tipo(valor, esperado):
    real = _tipo_de(valor)
    if esperado == "number":
        return real in ("number", "integer")
    return real == esperado


def revisar_schema(schema, ruta="$"):
    """Verifica que el schema sea usable. Lanza SchemaError si no."""
    if not isinstance(schema, dict):
        raise SchemaError(f"{ruta}: el schema debe ser un objeto JSON")

    desconocidas = set(schema) - VALIDADORES - ANOTACION
    if desconocidas:
        raise SchemaError(
            f"{ruta}: keyword(s) no soportada(s): {', '.join(sorted(desconocidas))}. "
            "Se rechazan para no dar por válido un dato sin haberlo chequeado."
        )

    if "type" in schema:
        tipos = schema["type"]
        tipos = [tipos] if isinstance(tipos, str) else tipos
        if not isinstance(tipos, list) or not tipos:
            raise SchemaError(f"{ruta}.type: debe ser string o lista de strings")
        validos = {"object", "array", "string", "number", "integer", "boolean", "null"}
        for t in tipos:
            if t not in validos:
                raise SchemaError(f"{ruta}.type: tipo desconocido {t!r}")

    if "format" in schema and schema["format"] not in FORMATOS:
        raise SchemaError(f"{ruta}.format: formato no soportado {schema['format']!r}")

    if "required" in schema and not isinstance(schema["required"], list):
        raise SchemaError(f"{ruta}.required: debe ser lista")

    if "properties" in schema:
        if not isinstance(schema["properties"], dict):
            raise SchemaError(f"{ruta}.properties: debe ser objeto")
        for nombre, sub in schema["properties"].items():
            revisar_schema(sub, f"{ruta}.properties.{nombre}")

    if "items" in schema:
        revisar_schema(schema["items"], f"{ruta}.items")

    ap = schema.get("additionalProperties")
    if ap is not None and not isinstance(ap, (bool, dict)):
        raise SchemaError(f"{ruta}.additionalProperties: debe ser boolean u objeto")
    if isinstance(ap, dict):
        revisar_schema(ap, f"{ruta}.additionalProperties")

    if "enum" in schema and not isinstance(schema["enum"], list):
        raise SchemaError(f"{ruta}.enum: debe ser lista")


def _formato_ok(valor, fmt):
    if not isinstance(valor, str):
        return True
    try:
        if fmt == "date":
            date.fromisoformat(valor)
        elif fmt == "date-time":
            datetime.fromisoformat(valor.replace("Z", "+00:00"))
        elif fmt == "uri":
            return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", valor))
        elif fmt == "email":
            return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", valor))
    except ValueError:
        return False
    return True


def validar(valor, schema, ruta="$", errores=None):
    """Devuelve lista de (ruta, mensaje)."""
    if errores is None:
        errores = []

    if "type" in schema:
        tipos = schema["type"]
        tipos = [tipos] if isinstance(tipos, str) else tipos
        if schema.get("nullable") and "null" not in tipos:
            tipos = tipos + ["null"]
        if not any(_coincide_tipo(valor, t) for t in tipos):
            errores.append((ruta, f"se esperaba {'|'.join(tipos)} y llegó {_tipo_de(valor)}"))
            return errores

    if valor is None:
        return errores

    if "enum" in schema and valor not in schema["enum"]:
        errores.append((ruta, f"valor {valor!r} fuera del enum permitido"))

    if isinstance(valor, str):
        if "minLength" in schema and len(valor) < schema["minLength"]:
            errores.append((ruta, f"largo {len(valor)} menor al mínimo {schema['minLength']}"))
        if "maxLength" in schema and len(valor) > schema["maxLength"]:
            errores.append((ruta, f"largo {len(valor)} mayor al máximo {schema['maxLength']}"))
        if "pattern" in schema and not re.search(schema["pattern"], valor):
            errores.append((ruta, f"no cumple el patrón {schema['pattern']!r}"))
        if "format" in schema and not _formato_ok(valor, schema["format"]):
            errores.append((ruta, f"{valor!r} no es un {schema['format']} válido"))

    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        if "minimum" in schema and valor < schema["minimum"]:
            errores.append((ruta, f"{valor} menor al mínimo {schema['minimum']}"))
        if "maximum" in schema and valor > schema["maximum"]:
            errores.append((ruta, f"{valor} mayor al máximo {schema['maximum']}"))
        if "exclusiveMinimum" in schema and valor <= schema["exclusiveMinimum"]:
            errores.append((ruta, f"{valor} debe ser mayor que {schema['exclusiveMinimum']}"))
        if "exclusiveMaximum" in schema and valor >= schema["exclusiveMaximum"]:
            errores.append((ruta, f"{valor} debe ser menor que {schema['exclusiveMaximum']}"))

    if isinstance(valor, list):
        if "minItems" in schema and len(valor) < schema["minItems"]:
            errores.append((ruta, f"cantidad {len(valor)} menor al mínimo {schema['minItems']}"))
        if "maxItems" in schema and len(valor) > schema["maxItems"]:
            errores.append((ruta, f"cantidad {len(valor)} mayor al máximo {schema['maxItems']}"))
        if schema.get("uniqueItems"):
            vistos = set()
            for i, item in enumerate(valor):
                clave = json.dumps(item, sort_keys=True, ensure_ascii=False)
                if clave in vistos:
                    errores.append((f"{ruta}[{i}]", "elemento duplicado"))
                vistos.add(clave)
        if "items" in schema:
            for i, item in enumerate(valor):
                validar(item, schema["items"], f"{ruta}[{i}]", errores)

    if isinstance(valor, dict):
        for campo in schema.get("required", []):
            if campo not in valor:
                errores.append((ruta, f"falta el campo obligatorio {campo!r}"))
        props = schema.get("properties", {})
        for nombre, sub in props.items():
            if nombre in valor:
                validar(valor[nombre], sub, f"{ruta}.{nombre}", errores)
        extra = set(valor) - set(props)
        ap = schema.get("additionalProperties", True)
        if ap is False:
            for nombre in sorted(extra):
                errores.append((f"{ruta}.{nombre}", "campo no permitido por el contrato"))
        elif isinstance(ap, dict):
            for nombre in sorted(extra):
                validar(valor[nombre], ap, f"{ruta}.{nombre}", errores)

    return errores


def _cargar(ruta):
    try:
        with open(ruta, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise SchemaError(f"no existe el archivo: {ruta}")
    except json.JSONDecodeError as exc:
        raise SchemaError(f"JSON inválido en {ruta}: {exc}")


def _salida_json(ok, errores, extra=None):
    payload = {"ok": ok, "total_errores": len(errores),
               "errores": [{"path": p, "mensaje": m} for p, m in errores]}
    if extra:
        payload.update(extra)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    max_errores = 20
    for f in list(flags):
        if f.startswith("--max-errores="):
            max_errores = int(f.split("=", 1)[1])
            flags.discard(f)

    if not args:
        print(__doc__.strip())
        return EXIT_ERROR

    comando = args[0]

    if comando == "contrato":
        if len(args) != 2:
            print("uso: validador contrato <schema.json>")
            return EXIT_ERROR
        try:
            schema = _cargar(args[1])
            revisar_schema(schema)
        except SchemaError as exc:
            if "--json" in flags:
                _salida_json(False, [("$", str(exc))])
            else:
                print(f"SCHEMA INVALIDO: {exc}")
            return EXIT_ERROR
        if "--json" in flags:
            _salida_json(True, [])
        else:
            print("SCHEMA OK")
        return EXIT_OK

    if comando != "validar" or len(args) != 3:
        print("uso: validador validar <schema.json> <datos.json>")
        return EXIT_ERROR

    try:
        schema = _cargar(args[1])
        revisar_schema(schema)
        datos = _cargar(args[2])
    except SchemaError as exc:
        if "--json" in flags:
            _salida_json(False, [("$", str(exc))])
        else:
            print(f"NO SE PUDO VALIDAR: {exc}")
        return EXIT_ERROR

    errores = validar(datos, schema)

    if "--json" in flags:
        _salida_json(not errores, errores)
    elif errores:
        print(f"INVALIDO: {len(errores)} error(es)")
        for path, msg in errores[:max_errores]:
            print(f"  {path}: {msg}")
        if len(errores) > max_errores:
            print(f"  ... y {len(errores) - max_errores} más")
    else:
        n = len(datos) if isinstance(datos, list) else 1
        print(f"VALIDO: {n} registro(s) cumplen el contrato")

    return EXIT_INVALID if errores else EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv))
