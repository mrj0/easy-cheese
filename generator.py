import os, re
from template import template
import jinja2
import simplejson as json
from wtforms import form, fields

safe_string = jinja2.Markup

SETUP_PY_TEMPLATE = 'setup_py.tpl'

python_file_pattern = re.compile('(.*)\.(py|pyc|pyo)$', re.I)
readme_file_pattern = re.compile('readme(\..*)?$', re.I)


FIELDS = ('name', 'version', 'description', 'long_description',
          'url', 'author', 'author_email', 'readme', 'modules', 'packages',)


def create_setup(client=None):
    """
    Use the file list from the source control client to
    instantiate a new Setup object.
    """

    setup = SetupDistutils()
    data = {}

    if client:
        data['name'] = client.name
        data['author'] = client.author
        data['url'] = client.url
        data['description'] = client.description

        packages = [os.path.dirname(f) for f in client.files if '__init__.' in f]
        data['packages'] = ' '.join(packages)

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
        data['modules'] = ' '.join(modules)

    setup.process(**data)
    return setup


class Setup(form.Form):
    author = fields.TextField()
    author_email = fields.TextField()
    name = fields.TextField()
    description = fields.TextField()
    version = fields.TextField()
    long_description = fields.TextAreaField()
    url = fields.TextField()
    modules = fields.TextField()
    packages = fields.TextField()

    def __init__(self, *args, **kwargs):
        super(Setup, self).__init__(*args, **kwargs)
        self.readme = None

    def as_hidden(self):
        data = self.data
        data['readme'] = self.readme

        return '<input name="previous" value="{}" type="hidden">'.format(
            jinja2.escape(json.dumps(data)),
        )


class SetupDistutils(Setup):
    def generate(self):
        return safe_string(template(SETUP_PY_TEMPLATE, setup=self))
