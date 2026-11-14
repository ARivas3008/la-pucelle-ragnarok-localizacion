#!/usr/bin/env python3
import unittest
from util import marker_list
class TestVariables(unittest.TestCase):
    def test_format_tags(self):
        src='Hola {0}, %s, <color=#FFFF00>foo</color>\\n{player}'
        good='Hola {0}, %s, <color=#FFFF00>amigo</color>\\n{player}'
        bad='Hola {0}, %s, <color=#FFF000>amigo</color>\\n{player}'
        self.assertEqual(marker_list(src),marker_list(good))
        self.assertNotEqual(marker_list(src),marker_list(bad))
    def test_masked_name(self):
        self.assertNotEqual(marker_list('??????'),marker_list('Ellie'))
    def test_ordinary_words(self):
        self.assertEqual(marker_list('Qué haces?'),marker_list('¿Qué estás haciendo?'))
if __name__=='__main__':unittest.main()
