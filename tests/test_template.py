# -*- coding: utf-8 -*-

import unittest
from template import pyquote

class TestTemplates(unittest.TestCase):
    def test_pyquote(self):
        self.assertEqual(u"u'testé'", pyquote(u'testé'))

if __name__ == '__main__':
    unittest.main()
