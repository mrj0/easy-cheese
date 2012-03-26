# -*- coding: utf-8 -*-

import unittest
from template import is_ascii, clean_identifiers, pyquote


class TestTemplates(unittest.TestCase):
    def test_clean_packages(self):
        self.assertEqual(['one', 'two'], clean_identifiers('one, two'))
        self.assertEqual(['one', 'two'], clean_identifiers('one two'))
        self.assertEqual(['one', 'two9'], clean_identifiers('one two9'))
        self.assertEqual(['one', 'two', 'three'], clean_identifiers('one two\nthree'))

    def test_pyquote(self):
        self.assertIsNone(pyquote(None))
        self.assertEqual("''", pyquote(''))
        self.assertEqual("'''one\ntwo'''", pyquote('one\ntwo'))
        self.assertEqual("'''one\n\'two'''", pyquote('one\n\'two'))
        self.assertEqual("'''one\n\\'''two'''", pyquote('one\n\'\'\'two'))
        self.assertEqual(u"u'testé'", pyquote(u'testé'))

    def test_is_ascii(self):
        self.assertTrue(is_ascii('adsf'))
        self.assertTrue(is_ascii(None))
        self.assertTrue(is_ascii(''))
        self.assertFalse(is_ascii(u'testé'))

if __name__ == '__main__':
    unittest.main()
