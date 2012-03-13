from template import template, pyquote
import jinja2

safe_string = jinja2.Markup

SETUP_PY_TEMPLATE = 'setup_py.tpl'


class Setup(object):
    def __init__(self):
        self.name = None
        self.description = None
        self.version = None
        self.long_description = None

        self.modules = []
        self.packages = []

    @property
    def required_fields(self):
        return (
            'name',
            'description',
            'version',
            'long_description',
        )

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


class SetupDistutils(Setup):
    def generate(self):
        return safe_string(template(SETUP_PY_TEMPLATE, setup=self))
