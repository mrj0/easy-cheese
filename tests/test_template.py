# -*- coding: utf-8 -*-

import unittest
from generator import Setup
from template import pyquote, is_ascii, clean_identifiers, _pyquote

class TestTemplates(unittest.TestCase):
    def test_clean_packages(self):
        self.assertEqual(['one', 'two'], clean_identifiers('one, two'))
        self.assertEqual(['one', 'two'], clean_identifiers('one two'))
        self.assertEqual(['one', 'two9'], clean_identifiers('one two9'))
        self.assertEqual(['one', 'two', 'three'], clean_identifiers('one two\nthree'))

    def test_pyquote(self):
        self.assertIsNone(_pyquote(None))
        self.assertEqual(u"u'testé'", _pyquote(u'testé'))
        self.assertEqual("''", _pyquote(''))

    def test_is_ascii(self):
        self.assertTrue(is_ascii('adsf'))
        self.assertTrue(is_ascii(None))
        self.assertTrue(is_ascii(''))
        self.assertFalse(is_ascii(u'testé'))

#    def test_setup_required(self): todo fix validation
#        s = Setup()
#        self.assertFalse(s.validate())
#        self.assertEqual(sorted(s.required_fields), sorted(s.errors.keys()))

if __name__ == '__main__':
    unittest.main()
