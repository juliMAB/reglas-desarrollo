"""Tests del validador. Solo stdlib: python3 -m unittest discover -s tests"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDADOR = os.path.join(RAIZ, "validador.py")

SCHEMA_VALIDO = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "vigente"],
        "properties": {
            "id": {"type": "string", "minLength": 1},
            "vigente": {"type": "boolean"},
            "fecha": {"type": "string", "format": "date-time"},
            "nota": {"type": ["string", "null"]},
        },
        "additionalProperties": True,
    },
}


def escribir(directorio, nombre, contenido):
    ruta = os.path.join(directorio, nombre)
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(contenido, fh)
    return ruta


def correr(*args):
    proc = subprocess.run(
        [sys.executable, VALIDADOR, *args],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


class ValidadorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.schema = escribir(self.dir, "schema.json", SCHEMA_VALIDO)

    def tearDown(self):
        self.tmp.cleanup()

    def test_dato_valido_sale_0(self):
        datos = escribir(self.dir, "d.json", [{"id": "a:1", "vigente": True}])
        codigo, salida = correr("validar", self.schema, datos)
        self.assertEqual(codigo, 0, salida)
        self.assertIn("VALIDO", salida)

    def test_array_vacio_es_valido(self):
        datos = escribir(self.dir, "d.json", [])
        codigo, salida = correr("validar", self.schema, datos)
        self.assertEqual(codigo, 0, salida)

    def test_campo_obligatorio_faltante_sale_1(self):
        datos = escribir(self.dir, "d.json", [{"id": "a:1"}])
        codigo, salida = correr("validar", self.schema, datos)
        self.assertEqual(codigo, 1, salida)
        self.assertIn("vigente", salida)

    def test_tipo_incorrecto_sale_1(self):
        datos = escribir(self.dir, "d.json", [{"id": "a:1", "vigente": "si"}])
        codigo, _ = correr("validar", self.schema, datos)
        self.assertEqual(codigo, 1)

    def test_bool_no_pasa_como_integer(self):
        schema = escribir(self.dir, "s2.json", {"type": "integer"})
        datos = escribir(self.dir, "d2.json", True)
        codigo, _ = correr("validar", schema, datos)
        self.assertEqual(codigo, 1)

    def test_fecha_invalida_sale_1(self):
        datos = escribir(self.dir, "d.json", [{"id": "a", "vigente": True, "fecha": "2026-13-45"}])
        codigo, salida = correr("validar", self.schema, datos)
        self.assertEqual(codigo, 1, salida)
        self.assertIn("date-time", salida)

    def test_null_permitido_por_tipo(self):
        datos = escribir(self.dir, "d.json", [{"id": "a", "vigente": True, "nota": None}])
        codigo, salida = correr("validar", self.schema, datos)
        self.assertEqual(codigo, 0, salida)

    def test_archivo_inexistente_sale_2(self):
        codigo, salida = correr("validar", self.schema, os.path.join(self.dir, "nada.json"))
        self.assertEqual(codigo, 2, salida)
        self.assertIn("no existe", salida)

    def test_json_roto_sale_2(self):
        ruta = os.path.join(self.dir, "roto.json")
        with open(ruta, "w", encoding="utf-8") as fh:
            fh.write("{ no es json")
        codigo, _ = correr("validar", self.schema, ruta)
        self.assertEqual(codigo, 2)

    def test_keyword_desconocida_sale_2(self):
        ruta = escribir(self.dir, "s3.json", {"type": "object", "require": ["x"]})
        datos = escribir(self.dir, "d3.json", {"x": 1})
        codigo, salida = correr("validar", ruta, datos)
        self.assertEqual(codigo, 2, salida)
        self.assertIn("require", salida)

    def test_comando_contrato_ok(self):
        codigo, salida = correr("contrato", self.schema)
        self.assertEqual(codigo, 0, salida)
        self.assertIn("SCHEMA OK", salida)

    def test_salida_json(self):
        datos = escribir(self.dir, "d.json", [{"vigente": True}])
        codigo, salida = correr("validar", self.schema, datos, "--json")
        self.assertEqual(codigo, 1)
        payload = json.loads(salida)
        self.assertFalse(payload["ok"])
        self.assertTrue(payload["errores"])
        self.assertIn("path", payload["errores"][0])

    def test_contrato_real_de_beneficios(self):
        base = os.path.join(
            os.path.expanduser("~"), "proyectos", "beneficios", "contratos", "descuentos", "v1.0.0"
        )
        schema = os.path.join(base, "schema.json")
        if not os.path.exists(schema):
            self.skipTest("contrato de beneficios no presente")
        for nombre, esperado in (("ejemplo.json", 0), ("vacio.json", 0)):
            codigo, salida = correr("validar", schema, os.path.join(base, nombre))
            self.assertEqual(codigo, esperado, f"{nombre}: {salida}")


if __name__ == "__main__":
    unittest.main()
