import os, re
from template import template, pyquote
import jinja2
import simplejson as json

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

    if client:
        setup.name = client.name
        setup.author = client.author
        setup.url = client.url
        setup.description = client.description

        setup.packages = [os.path.dirname(f) for f in client.files if '__init__.' in f]

        # look for files not in a package to add to py_modules in setup
        # find README.* files, first one wins
        for filename in client.files:
            match = re.match(python_file_pattern, filename)
            if match:
                package = os.path.dirname(filename)
                module = match.groups()[0]
                if not module.endswith('setup') and package not in setup.packages:
                    setup.modules.append(module.replace('/', '.'))

            if not setup.readme:
                match = re.match(readme_file_pattern, filename)
                if match:
                    setup.readme = filename

    return setup


class Setup(object):
    def __init__(self):
        self.author = None
        self.author_email = None
        self.name = None
        self.description = None
        self.version = None
        self.long_description = None
        self.readme = None
        self.url = None

        self.modules = []
        self.packages = []

    @property
    def required_fields(self):
        return (
            'author',
            'author_email',
            'name',
            'description',
            'version',
        )

    @property
    def setup_fields(self):
        fields = (
            'author',
            'author_email',
            'url',
            'name',
            'description',
            'version',
        )

        return map(lambda x: (x, getattr(self, x)), fields)

    def required(self):
        return map(lambda x: (x, getattr(self, x),), self.required_fields)

    @property
    def module_str(self):
        return ', '.join(map(pyquote, self.modules))

    @property
    def package_str(self):
        return ', '.join(map(pyquote, self.packages))

    def is_valid(self):
        self.errors = {}
        for field in self.required_fields:
            value = getattr(self, field)
            if not value:
                self.errors[field] = '{field} is required'.format(field=field)
        return not bool(self.errors)

    def as_hidden(self):
        return '<input name="previous" value="{}" type="hidden">'.format(
            jinja2.escape(json.dumps(self.__dict__)),
        )


class SetupDistutils(Setup):
    def generate(self):
        return safe_string(template(SETUP_PY_TEMPLATE, setup=self))
