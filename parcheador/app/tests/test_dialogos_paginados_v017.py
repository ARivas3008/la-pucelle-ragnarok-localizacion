"""Regresión v0.17: dos cuadros de una misma frase, sin editar opcodes."""
import sys
import unittest
from collections import defaultdict
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from construir_parche import planificar_paginados, to_full
from fuentes_es import encode_es


class PruebasDeDialogosPaginados(unittest.TestCase):
    def caso(self, frontera=b"\x00\x02\x01"):
        a = to_full("HOLA!").encode("cp932")
        b = to_full("MUNDO").encode("cp932")
        raw = b"\x01" + a + frontera + b + b"\x00"
        resource = "ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/talk01_jp.dat"
        rows = [
            dict(unit_id="100", grupo_id="X", recurso=resource,
                 offset="1", original="HOLA!"),
            dict(unit_id="101", grupo_id="X", recurso=resource,
                 offset=str(1 + len(a) + len(frontera)), original="MUNDO")
        ]
        groups = defaultdict(list)
        for r in rows:
            groups[r["grupo_id"]].append(r)
        reviews = {"X": dict(estado="revisado", es_revisado="MUY BIEN")}
        return rows, {resource: bytearray(raw)}, groups, reviews

    def test_paginas_separadas_sin_cambiar_opcodes(self):
        rows, source, groups, reviews = self.caso()
        before = bytes(next(iter(source.values())))
        answers, rejects = planificar_paginados(
            rows, source, groups, reviews, False, True, {}, {})
        self.assertEqual(set(answers), {"100", "101"})
        self.assertFalse(rejects)
        self.assertEqual(bytes(next(iter(source.values()))), before)
        self.assertEqual([answers[x][1] for x in ("100", "101")], ["MUY", "BIEN"])
        self.assertEqual([len(answers[x][2]) for x in ("100", "101")], [10, 10])

    def test_separador_no_verificado_se_rechaza(self):
        rows, source, groups, reviews = self.caso(b"\x00\x03\x01")
        answers, _ = planificar_paginados(
            rows, source, groups, reviews, False, True, {}, {})
        self.assertFalse(answers)

    def test_revisiones_ausentes_no_se_inventan(self):
        rows, source, groups, _ = self.caso()
        answers, rejected = planificar_paginados(
            rows, source, groups, {}, False, True, {}, {})
        self.assertFalse(answers)
        self.assertEqual(set(rejected), {"100", "101"})


if __name__ == "__main__":
    unittest.main()
