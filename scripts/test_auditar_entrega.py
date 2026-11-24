"""Regresiones de la auditoría ROM-008; no requieren ISO comercial."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import auditar_entrega as audit

class TestScope(unittest.TestCase):
    def test_scope_uses_global_denominator(self):
        result=audit.coverage_scope({'TALK_BLOQUE_INSERTADO': 8,'DLC_NO_APORTADO': 2})
        self.assertEqual(result['unidades_total'],10)
        self.assertEqual(result['unidades_en_alcance'],8)
        self.assertEqual(result['porcentaje_unidades_tecnicas'],80.0)
        self.assertEqual(result['porcentaje_en_alcance'],100.0)

    def test_pending_and_unchanged_are_not_insertions(self):
        result=audit.coverage_scope({'TALK_PENDIENTE': 1,'SIN_CAMBIO_COINCIDE_REVISION': 1,
                                     'SCRIPT_INSERTADO': 1,'CAMPO_COINCIDE_REVISION': 1,
                                     'GRAFICO_PENDIENTE_REVISION_VISUAL': 1})
        self.assertEqual(result['unidades_insertadas_verificadas'],2)
        self.assertEqual(result['porcentaje_unidades_tecnicas'],40.0)

    def test_empty_scope(self):
        self.assertIsNone(audit.coverage_scope({'DLC_NO_APORTADO': 1})['porcentaje_en_alcance'])
        self.assertIsNone(audit.coverage_scope({})['porcentaje_unidades_tecnicas'])

    def test_base_without_dlc(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(audit.resolve_dlc(Path(tmp),None))

    def test_existing_dlc_cannot_be_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent=Path(tmp)
            (parent/'ULJS00244').mkdir()
            with self.assertRaises(ValueError):
                audit.resolve_dlc(parent,None)

    def test_incomplete_dlc_pair_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent=Path(tmp)
            source=parent/'source'
            dest=parent/'ULJS00244'
            for directory in (source,dest):
                directory.mkdir()
                for n in range(4):
                    (directory/f'DL_JP_{n:02d}.EDAT').touch()
            self.assertEqual(audit.resolve_dlc(parent,source),dest)
            (dest/'DL_JP_03.EDAT').unlink()
            with self.assertRaises(ValueError):
                audit.resolve_dlc(parent,source)

    def test_load_base_reads_no_edat(self):
        class Image:
            def __init__(self,path): pass
            def records(self):
                return [('/PSP_GAME/USRDIR/START_JP.LZS',0,1,None),
                        ('/PSP_GAME/SYSDIR/EBOOT.BIN',1,1,None)]
            def read(self,offset,length):
                return b'x' if offset==0 else b'y'
        with patch.object(audit.c,'Image',Image),patch.object(audit,'lzs_decompress',return_value=b'raw'),patch.object(audit.c,'members_from_dat',return_value={'table.dat':b'z'}):
            self.assertEqual(audit.load(Path('fake.iso')),{'ISO_START/table.dat':b'z','ISO/PSP_GAME/SYSDIR/EBOOT.BIN':b'y'})

if __name__=='__main__':unittest.main()
