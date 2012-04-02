import re
from wtforms import StringField

identifiers = re.compile(r'[a-zA-Z0-9_]+')

packages = re.compile(r'[a-zA-Z0-9_/]+')

requires = re.compile(r'([a-z0-9_]+=?=?[a-z0-9\.\-_]*)', re.I)


class PythonStringFieldBase(StringField):
    """
    A Text field (``<input type="text">``) that can hold multiple values.

    Values are escaped Python strings using ``pyquote``
    """

    def __init__(self, pattern, *args, **kwargs):
        super(PythonStringFieldBase, self).__init__(*args, **kwargs)
        self.pattern = pattern

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = ' '.join(valuelist)
        else:
            self.data = u''

    def as_list(self):
        return re.findall(self.pattern, self._value())


class ModulesField(PythonStringFieldBase):
    def __init__(self, *args, **kwargs):
        super(ModulesField, self).__init__(identifiers, *args, **kwargs)


class RequiresField(PythonStringFieldBase):
    def __init__(self, *args, **kwargs):
        super(RequiresField, self).__init__(requires, *args, **kwargs)


class PackagesField(PythonStringFieldBase):
    def __init__(self, *args, **kwargs):
        super(PackagesField, self).__init__(packages, *args, **kwargs)
