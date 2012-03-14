# -*- coding: utf-8 -*-

import unittest
from generator import Setup
from template import pyquote, is_ascii

class TestTemplates(unittest.TestCase):
    def test_pyquote(self):
        self.assertIsNone(pyquote(None))
        self.assertEqual(u"u'testé'", pyquote(u'testé'))
        self.assertEqual("''", pyquote(''))

    def test_is_ascii(self):
        self.assertTrue(is_ascii('adsf'))
        self.assertTrue(is_ascii(None))
        self.assertTrue(is_ascii(''))
        self.assertFalse(is_ascii(u'testé'))

    def test_setup_required(self):
        s = Setup()
        self.assertFalse(s.is_valid())
        self.assertEqual(sorted(s.required_fields), sorted(s.errors.keys()))

if __name__ == '__main__':
    unittest.main()
