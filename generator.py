import os
import re
from template import template
import jinja2
import simplejson as json
from wtforms import form, fields
import logging

log = logging.getLogger(__name__)

safe_string = jinja2.Markup

SETUP_PY_TEMPLATE = 'setup_py.tpl'

python_file_pattern = re.compile('(.*)\.(py|pyc|pyo)$', re.I)
readme_file_pattern = re.compile('readme(\..*)?$', re.I)

from trove import all_classifiers
license_choices = \
    [('', '')] + \
    [tuple([c.split(' :: ')[-1]] * 2) for c in all_classifiers
                    if c.startswith('License :: ')]
classifier_choices = [tuple([c] * 2) for c in all_classifiers
                    if not c.startswith('License :: ')]


def create_setup(client=None):
    """
    Use the file list from the source control client to
    instantiate a new Setup object.
    """

    setup = SetupDistutils()

    packages = []
    modules = []

    if client:
        packages = [os.path.dirname(f)
                    for f in client.files if '__init__.' in f]

        # look for files not in a package to add to py_modules in setup
        # find README.* files, first one wins
        modules = []
        for filename in client.files:
            match = re.match(python_file_pattern, filename)
            if match:
                package = os.path.dirname(filename)
                module = match.groups()[0]
                if not module.endswith('setup') and package not in packages:
                    modules.append(module.replace('/', '.'))

            if not setup.readme:
                match = re.match(readme_file_pattern, filename)
                if match:
                    setup.readme = filename

    setup.process(None, **client.discovered)
    setup.py_modules.data = modules
    setup.packages.data = packages
    return setup


class Setup(form.Form):
    author = fields.TextField()
    author_email = fields.TextField()
    name = fields.TextField()
    description = fields.TextField()
    version = fields.TextField()
    long_description = fields.TextAreaField()
    url = fields.TextField()
    license = fields.SelectField(choices=license_choices)
    classifiers = fields.SelectMultipleField(choices=classifier_choices)

    # lists
    py_modules = fields.TextField()
    packages = fields.TextField()

    def __init__(self, *args, **kwargs):
        super(Setup, self).__init__(*args, **kwargs)
        self.readme = None
        if self.license.data == 'None':
            self.license.data = None
        if self.classifiers.data == 'None':
            self.classifiers.data = None

    def process(self, formdata=None, obj=None, **kwargs):
        super(Setup, self).process(formdata=formdata, obj=obj, **kwargs)

        # wtforms bugs?
        if self.license.data == 'None':
            self.license.data = None
        if self.classifiers.data == 'None':
            self.classifiers.data = None

    def as_hidden(self):
        data = self.data
        data['readme'] = self.readme

        return '<input name="previous" value="{}" type="hidden">'.format(
            jinja2.escape(json.dumps(data)),
        )


class SetupDistutils(Setup):

    def generate(self, executable=False, under_test=False):
        try:
            return safe_string(template(SETUP_PY_TEMPLATE,
                                        setup=self,
                                        executable=executable,
                                        under_test=under_test))
        except Exception:
            log.exception('Failed to generate setup.py')
            return 'Error generating setup.py'
