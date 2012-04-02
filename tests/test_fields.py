import unittest
from bottle import FormsDict
from wtforms import form
from fields import ModulesField, RequiresField, PackagesField


class TestForm(form.Form):
    identifiers = ModulesField()
    requires = RequiresField()
    packages = PackagesField()


class TestFields(unittest.TestCase):
    def test_html(self):
        data = FormsDict()
        data['identifiers'] = 'one'
        data['identifiers'] = 'two'
        form = TestForm(formdata=data)
        self.assertTrue('one two' in unicode(form.identifiers))

    def test_list(self):
        data = FormsDict()
        data['identifiers'] = 'one'
        data['identifiers'] = 'two'
        form = TestForm(formdata=data)

        self.assertEqual(['one', 'two'], form.identifiers.as_list())

    def test_requires(self):
        data = FormsDict()
        data['requires'] = 'Jinja2'
        data['requires'] = 'Jinja3==3.0.0-dev_one'
        form = TestForm(formdata=data)

        expected = ['Jinja2', 'Jinja3==3.0.0-dev_one']
        self.assertEqual(expected, form.requires.as_list())
        self.assertEqual(' '.join(expected), form.requires._value())

    def test_requires(self):
        data = FormsDict()
        data['packages'] = 'one'
        data['packages'] = 'one/two_test'
        form = TestForm(formdata=data)

        expected = ['one', 'one/two_test']
        self.assertEqual(expected, form.packages.as_list())
        self.assertEqual(' '.join(expected), form.packages._value())


if __name__ == '__main__':
    unittest.main()
